"""CedFRA — Generatore Documenti Retribuzioni.

Applicazione Tkinter per la generazione automatica dei documenti Word
mensili (Pagamento e Mese Anno) per i dipendenti Marine Interiors.

v1.2 — Sviluppata da Simone Robbiani
"""

import datetime
import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Aggiungi la cartella dell'app al path
APP_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, APP_DIR)

from amount_converter import (
    formatta_importo_mese,
    formatta_importo_pagamento,
    importo_in_cifre,
    importo_in_lettere,
)
from constants import MESI_FRANCESE, MESI_ITALIANO
from config_manager import ConfigManager
from date_utils import (
    calcola_data_pagamento,
    formatta_data_estesa,
    formatta_data_italiana,
    formatta_data_protocollo,
)
from pdf_extractor import estrai_dati_cedolino
from ui.config_panel import ConfigPanel
from word_generator import (
    costruisci_nome_file_mese,
    costruisci_nome_file_pagamento,
    genera_mese,
    genera_pagamento,
)

APP_VERSION = "1.2.2"
APP_AUTHOR = "Simone Robbiani"

# Colori brand Marine Interiors
BRAND_NAVY = "#1C3D71"
BRAND_NAVY_LIGHT = "#2A5298"
BRAND_NAVY_DARK = "#142C52"
BRAND_GOLD = "#C8A864"
COLOR_WHITE = "#FFFFFF"
COLOR_BG = "#F2F4F7"
COLOR_CARD = "#FFFFFF"
COLOR_TEXT = "#1E1E1E"
COLOR_TEXT_MUTED = "#6B7280"
COLOR_BORDER = "#D1D5DB"
COLOR_SUCCESS = "#16A34A"
COLOR_LOG_BG = "#F8F9FA"
COLOR_WARNING = "#F59E0B"
COLOR_DANGER = "#DC2626"


class CedFRAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CedFRA \u2014 Marine Interiors")
        self.root.geometry("1100x700")
        self.root.resizable(True, True)
        self.root.configure(bg=COLOR_BG)

        # Config manager
        self.config_mgr = ConfigManager(APP_DIR)
        self.config = self.config_mgr.load_config()

        # Icona finestra
        logo_path = os.path.join(APP_DIR, "assets", "logo.png")
        if os.path.exists(logo_path):
            try:
                self._logo_icon = tk.PhotoImage(file=logo_path)
                self.root.iconphoto(False, self._logo_icon)
            except tk.TclError:
                pass

        # Dati estratti dal PDF
        self.dati_pdf = None
        self.dati_dipendente = None
        self.data_pagamento = None

        # Path ultimi documenti generati
        self.ultimo_path_pag = None
        self.ultimo_path_mese = None

        # Pannello configurazione
        self.config_panel = None

        self._crea_interfaccia()
        self._log("Applicazione avviata. Caricare un PDF cedolino per iniziare.")

    # ── Helper per creare widget stilizzati ──────────────────────────

    def _make_card(self, parent, **grid_kw):
        card = tk.Frame(parent, bg=COLOR_CARD, highlightbackground=COLOR_BORDER,
                        highlightthickness=1, padx=16, pady=12)
        card.grid(**grid_kw)
        return card

    def _section_title(self, parent, text, row):
        frame = tk.Frame(parent, bg=COLOR_CARD)
        frame.grid(row=row, column=0, columnspan=3, sticky="ew", pady=(12, 6))
        accent = tk.Frame(frame, bg=BRAND_NAVY, width=4, height=16)
        accent.pack(side="left", padx=(0, 8))
        tk.Label(frame, text=text, font=("Segoe UI Semibold", 10),
                 bg=COLOR_CARD, fg=BRAND_NAVY).pack(side="left")

    def _label(self, parent, text, row, col=0, **kw):
        font = kw.pop("font", ("Segoe UI", 9))
        fg = kw.pop("fg", COLOR_TEXT_MUTED)
        lbl = tk.Label(parent, text=text, font=font, bg=COLOR_CARD, fg=fg, anchor="e")
        lbl.grid(row=row, column=col, sticky="e", padx=(0, 10), pady=2)
        return lbl

    def _value_label(self, parent, var, row, col=1, colspan=2):
        lbl = tk.Label(parent, textvariable=var, font=("Segoe UI Semibold", 9),
                       bg=COLOR_CARD, fg=COLOR_TEXT, anchor="w")
        lbl.grid(row=row, column=col, columnspan=colspan, sticky="w", pady=2)
        return lbl

    def _styled_button(self, parent, text, command, bg=BRAND_NAVY, fg=COLOR_WHITE,
                       font=("Segoe UI Semibold", 10), **kw):
        btn = tk.Button(parent, text=text, font=font, bg=bg, fg=fg,
                        activebackground=BRAND_NAVY_LIGHT, activeforeground=COLOR_WHITE,
                        relief="flat", cursor="hand2", command=command, **kw)
        return btn

    # ── Interfaccia principale ───────────────────────────────────────

    def _crea_interfaccia(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Container esterno
        outer = tk.Frame(self.root, bg=COLOR_BG)
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_rowconfigure(1, weight=1)
        outer.grid_columnconfigure(0, weight=1)

        # ══════ HEADER BAR ══════
        header = tk.Frame(outer, bg=BRAND_NAVY, height=72)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        top_accent = tk.Frame(header, bg=BRAND_GOLD, height=3)
        top_accent.grid(row=0, column=0, columnspan=4, sticky="ew")

        # Logo
        logo_path = os.path.join(APP_DIR, "assets", "logo_header.png")
        if os.path.exists(logo_path):
            try:
                self._logo_img = tk.PhotoImage(file=logo_path)
                tk.Label(header, image=self._logo_img, bg=BRAND_NAVY,
                         borderwidth=0).grid(row=1, column=0, padx=(20, 16), pady=12, sticky="w")
            except tk.TclError:
                self._logo_img = None
                tk.Label(header, text="MARINE INTERIORS",
                         font=("Segoe UI Black", 14), bg=BRAND_NAVY,
                         fg=COLOR_WHITE).grid(row=1, column=0, padx=(20, 16), pady=12, sticky="w")
        else:
            tk.Label(header, text="MARINE INTERIORS",
                     font=("Segoe UI Black", 14), bg=BRAND_NAVY,
                     fg=COLOR_WHITE).grid(row=1, column=0, padx=(20, 16), pady=12, sticky="w")

        # Titolo
        title_frame = tk.Frame(header, bg=BRAND_NAVY)
        title_frame.grid(row=1, column=1, sticky="w")
        tk.Label(title_frame, text="CedFRA",
                 font=("Segoe UI", 16, "bold"), bg=BRAND_NAVY,
                 fg=COLOR_WHITE).pack(anchor="w")
        tk.Label(title_frame, text="Generatore Documenti Retribuzioni",
                 font=("Segoe UI", 9), bg=BRAND_NAVY,
                 fg="#A8BFD8").pack(anchor="w")

        # Pulsante Config
        self.btn_config = self._styled_button(
            header, text="\u2699 Configurazione", command=self._toggle_sidebar,
            bg=BRAND_GOLD, fg=BRAND_NAVY_DARK, font=("Segoe UI Semibold", 9),
            padx=12, pady=6,
        )
        self.btn_config.grid(row=1, column=2, padx=(10, 10), sticky="e")

        # ══════ CORPO ══════
        body = tk.Frame(outer, bg=COLOR_BG, padx=20, pady=16)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)

        self._crea_main_panel(body)

        # ══════ FOOTER ══════
        footer = tk.Frame(outer, bg=BRAND_NAVY_DARK, height=32)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_columnconfigure(1, weight=1)

        version_lbl = tk.Label(footer, text=f"v{APP_VERSION}",
                 font=("Segoe UI", 8, "underline"), bg=BRAND_NAVY_DARK,
                 fg="#8BA4C4", pady=6, cursor="hand2")
        version_lbl.grid(row=0, column=0, padx=(16, 0), sticky="w")
        version_lbl.bind("<Button-1>", lambda e: self._apri_changelog())

        tk.Label(footer, text="Marine Interiors S.p.A.",
                 font=("Segoe UI", 8), bg=BRAND_NAVY_DARK,
                 fg="#8BA4C4", pady=6).grid(row=0, column=1)
        tk.Label(footer, text=f"Sviluppata da S. Robbiani",
                 font=("Segoe UI", 8), bg=BRAND_NAVY_DARK,
                 fg="#A8BFD8", pady=6).grid(row=0, column=2, padx=(0, 16), sticky="e")

    def _crea_main_panel(self, parent):
        # ── Pulsante carica PDF ──
        btn_frame = tk.Frame(parent, bg=COLOR_BG)
        btn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        btn_frame.grid_columnconfigure(0, weight=1)

        self.btn_carica = self._styled_button(
            btn_frame, text="  Carica PDF cedolino  ", command=self._carica_pdf,
            font=("Segoe UI Semibold", 11), padx=20, pady=10,
        )
        self.btn_carica.grid(row=0, column=0, sticky="ew")

        # ── Card: Dati dal cedolino ──
        card1 = self._make_card(parent, row=1, column=0, sticky="ew", pady=(0, 10))
        card1.grid_columnconfigure(1, weight=1)
        self._section_title(card1, "Dati dal cedolino", 0)

        fields = [
            ("Dipendente:", "var_dipendente", 1),
            ("Mese / Anno:", "var_mese_anno", 2),
            ("Importo netto:", "var_importo", 3),
            ("In lettere:", "var_lettere", 4),
        ]
        for text, attr, r in fields:
            self._label(card1, text, r)
            var = tk.StringVar(value="\u2014")
            setattr(self, attr, var)
            self._value_label(card1, var, r)

        # ── Card: Dati protocollo ──
        card2 = self._make_card(parent, row=2, column=0, sticky="ew", pady=(0, 10))
        card2.grid_columnconfigure(1, weight=1)
        self._section_title(card2, "Dati protocollo", 0)

        self._label(card2, "N. Protocollo:", 1)
        prot_frame = tk.Frame(card2, bg=COLOR_CARD)
        prot_frame.grid(row=1, column=1, columnspan=2, sticky="w", pady=2)
        self.entry_prot_num = tk.Entry(prot_frame, width=8, font=("Segoe UI", 9),
                                       relief="solid", bd=1,
                                       highlightcolor=BRAND_NAVY, highlightthickness=1)
        self.entry_prot_num.pack(side="left")
        tk.Label(prot_frame, text="/", font=("Segoe UI Semibold", 9),
                 bg=COLOR_CARD, fg=COLOR_TEXT).pack(side="left", padx=(2, 2))
        self.entry_prot_anno = tk.Entry(prot_frame, width=5, font=("Segoe UI", 9),
                                        relief="solid", bd=1,
                                        highlightcolor=BRAND_NAVY, highlightthickness=1)
        self.entry_prot_anno.pack(side="left")
        self.entry_prot_anno.insert(0, str(datetime.date.today().year))

        self._label(card2, "Data protocollo:", 2)
        data_frame = tk.Frame(card2, bg=COLOR_CARD)
        data_frame.grid(row=2, column=1, columnspan=2, sticky="w", pady=2)
        self.entry_prot_data = tk.Entry(data_frame, width=12, font=("Segoe UI", 9),
                                        relief="solid", bd=1,
                                        highlightcolor=BRAND_NAVY, highlightthickness=1)
        self.entry_prot_data.pack(side="left")
        tk.Label(data_frame, text="GG/MM/AAAA", font=("Segoe UI", 8),
                 bg=COLOR_CARD, fg=COLOR_TEXT_MUTED).pack(side="left", padx=(8, 0))

        self._label(card2, "Descrizione:", 3)
        tk.Label(card2, text="MI-PER", font=("Segoe UI Semibold", 9),
                 bg=COLOR_CARD, fg=COLOR_TEXT).grid(row=3, column=1,
                                                      columnspan=2, sticky="w", pady=2)

        # ── Card: Data pagamento ──
        card3 = self._make_card(parent, row=3, column=0, sticky="ew", pady=(0, 10))
        card3.grid_columnconfigure(1, weight=1)
        self._section_title(card3, "Data pagamento", 0)

        self._label(card3, "Data valuta:", 1)
        self.var_data_pagamento = tk.StringVar(value="\u2014")
        self._value_label(card3, self.var_data_pagamento, 1)

        self._label(card3, "Modifica data:", 2)
        ovr_frame = tk.Frame(card3, bg=COLOR_CARD)
        ovr_frame.grid(row=2, column=1, columnspan=2, sticky="w", pady=2)
        self.entry_data_override = tk.Entry(ovr_frame, width=12,
                                             font=("Segoe UI", 9), relief="solid",
                                             bd=1, highlightcolor=BRAND_NAVY,
                                             highlightthickness=1)
        self.entry_data_override.pack(side="left")
        tk.Label(ovr_frame, text="GG/MM/AAAA  (vuoto = auto)",
                 font=("Segoe UI", 8), bg=COLOR_CARD,
                 fg=COLOR_TEXT_MUTED).pack(side="left", padx=(8, 0))

        # ── Pulsanti azione ──
        btns = tk.Frame(parent, bg=COLOR_BG)
        btns.grid(row=4, column=0, sticky="ew", pady=(4, 10))
        btns.grid_columnconfigure(0, weight=1)
        btns.grid_columnconfigure(1, weight=1)
        btns.grid_columnconfigure(2, weight=1)

        self.btn_genera = tk.Button(
            btns, text="Genera documenti",
            font=("Segoe UI Semibold", 10), bg="#B0B0B0", fg=COLOR_WHITE,
            activebackground="#15803D", activeforeground=COLOR_WHITE,
            relief="flat", cursor="hand2", padx=16, pady=8,
            state="disabled", disabledforeground=COLOR_WHITE,
            command=self._genera_documenti,
        )
        self.btn_genera.grid(row=0, column=0, sticky="ew", padx=(0, 4))

        self.btn_apri_pag = tk.Button(
            btns, text="Apri Pagamento",
            font=("Segoe UI", 10), bg=COLOR_CARD, fg=BRAND_NAVY,
            activebackground=COLOR_BG, activeforeground=BRAND_NAVY_DARK,
            relief="solid", bd=1, cursor="hand2", padx=16, pady=8,
            state="disabled", disabledforeground=COLOR_TEXT_MUTED,
            command=self._apri_ultimo_pagamento,
        )
        self.btn_apri_pag.grid(row=0, column=1, sticky="ew", padx=(4, 4))

        self.btn_apri_mese = tk.Button(
            btns, text="Apri Mese",
            font=("Segoe UI", 10), bg=COLOR_CARD, fg=BRAND_NAVY,
            activebackground=COLOR_BG, activeforeground=BRAND_NAVY_DARK,
            relief="solid", bd=1, cursor="hand2", padx=16, pady=8,
            state="disabled", disabledforeground=COLOR_TEXT_MUTED,
            command=self._apri_ultimo_mese,
        )
        self.btn_apri_mese.grid(row=0, column=2, sticky="ew", padx=(4, 0))

        # ── Card: Documenti generati ──
        self.card_docs = self._make_card(parent, row=5, column=0, sticky="ew", pady=(0, 6))
        self.card_docs.grid_remove()  # nascosta di default
        self.card_docs.grid_columnconfigure(1, weight=1)
        self._section_title(self.card_docs, "Ultimi documenti generati", 0)
        self.var_doc_pag = tk.StringVar(value="—")
        self.var_doc_mese = tk.StringVar(value="—")
        self._label(self.card_docs, "Pagamento:", 1)
        self._value_label(self.card_docs, self.var_doc_pag, 1)
        self._label(self.card_docs, "Mese:", 2)
        self._value_label(self.card_docs, self.var_doc_mese, 2)

        # ── Card: Log ──
        card_log = self._make_card(parent, row=6, column=0, sticky="ew", pady=(0, 6))
        card_log.grid_columnconfigure(0, weight=1)
        self._section_title(card_log, "Log operazioni", 0)

        log_frame = tk.Frame(card_log, bg=COLOR_CARD)
        log_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(4, 0))
        log_frame.grid_columnconfigure(0, weight=1)

        self.text_log = tk.Text(
            log_frame, height=8, font=("Consolas", 9),
            bg=COLOR_LOG_BG, fg=COLOR_TEXT, relief="solid", bd=1,
            highlightthickness=0, padx=8, pady=6, state="disabled",
        )
        self.text_log.grid(row=0, column=0, sticky="ew")

        scrollbar = tk.Scrollbar(log_frame, orient="vertical",
                                  command=self.text_log.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.text_log.configure(yscrollcommand=scrollbar.set)

        self.text_log.tag_configure("timestamp", foreground=COLOR_TEXT_MUTED)
        self.text_log.tag_configure("success", foreground=COLOR_SUCCESS)
        self.text_log.tag_configure("error", foreground=COLOR_DANGER)

    # ── Configurazione ───────────────────────────────────────────────

    def _toggle_sidebar(self):
        if self.config_panel is not None and self.config_panel.is_open():
            self.config_panel.close()
            self.config_panel = None
        else:
            self.config_panel = ConfigPanel(
                self.root, self.config_mgr, log_callback=self._log
            )

    def _apri_changelog(self):
        win = tk.Toplevel(self.root)
        win.title(f"CedFRA — Changelog v{APP_VERSION}")
        win.geometry("520x420")
        win.transient(self.root)

        hdr = tk.Frame(win, bg=BRAND_NAVY, height=40)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"Changelog v{APP_VERSION}", font=("Segoe UI Semibold", 11),
                 bg=BRAND_NAVY, fg=COLOR_WHITE).pack(side="left", padx=12, pady=8)
        tk.Button(hdr, text="X", font=("Segoe UI", 10), bg=BRAND_NAVY, fg=COLOR_WHITE,
                  relief="flat", cursor="hand2", command=win.destroy,
                  width=3).pack(side="right", padx=6, pady=4)

        tree = ttk.Treeview(win, columns=("version", "date", "type", "desc"),
                            show="headings", height=18)
        tree.heading("version", text="Ver.")
        tree.heading("date", text="Data")
        tree.heading("type", text="Tipo")
        tree.heading("desc", text="Descrizione")
        tree.column("version", width=50)
        tree.column("date", width=80)
        tree.column("type", width=55)
        tree.column("desc", width=300)

        sb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        changelog = self.config_mgr.get_changelog()
        for entry in changelog:
            for change in entry.get("changes", []):
                tree.insert("", "end", values=(
                    entry.get("version", ""),
                    entry.get("date", ""),
                    change.get("type", ""),
                    change.get("desc", ""),
                ))

    # ── Logica applicativa ───────────────────────────────────────────

    def _log(self, messaggio: str):
        ora = datetime.datetime.now().strftime("%H:%M:%S")
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log su UI
        self.text_log.configure(state="normal")
        self.text_log.insert("end", f"[{ora}] ", "timestamp")
        if "ERRORE" in messaggio:
            self.text_log.insert("end", f"{messaggio}\n", "error")
        elif "Generato:" in messaggio or "completata" in messaggio:
            self.text_log.insert("end", f"{messaggio}\n", "success")
        else:
            self.text_log.insert("end", f"{messaggio}\n")
        self.text_log.see("end")
        self.text_log.configure(state="disabled")

        # Log su file (giornaliero, apertura breve per compatibilità OneDrive)
        try:
            log_path = os.path.join(
                self.log_dir,
                datetime.date.today().strftime("cedfra_%Y-%m-%d.log"),
            )
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"[{ts}] {messaggio}\n")
        except Exception:
            pass

    def _carica_pdf(self):
        filepath = filedialog.askopenfilename(
            title="Seleziona il PDF del cedolino",
            filetypes=[("PDF files", "*.pdf")],
            initialdir=os.path.dirname(APP_DIR),
        )
        if not filepath:
            return

        try:
            dati = estrai_dati_cedolino(filepath)
        except ValueError as e:
            messagebox.showerror("Errore", str(e))
            self._log(f"ERRORE: {e}")
            return

        cognome = dati["cognome"]
        dipendenti_attivi = self.config_mgr.get_dipendenti_attivi()
        if cognome not in dipendenti_attivi:
            messagebox.showerror(
                "Errore",
                f"Dipendente '{cognome}' non trovato nella configurazione.\n"
                f"Dipendenti configurati: {', '.join(dipendenti_attivi.keys())}",
            )
            self._log(f"ERRORE: Dipendente '{cognome}' non configurato.")
            return

        self.dati_pdf = dati
        self.dati_dipendente = dipendenti_attivi[cognome]

        # Reset stato documenti precedenti
        self.ultimo_path_pag = None
        self.ultimo_path_mese = None
        self.var_doc_pag.set("\u2014")
        self.var_doc_mese.set("\u2014")
        self.card_docs.grid_remove()
        self.btn_apri_pag.configure(state="disabled")
        self.btn_apri_mese.configure(state="disabled")

        nome_completo = f"{dati['cognome']} {dati['nome']}"
        mese_nome = MESI_ITALIANO[dati["mese"] - 1].capitalize()
        self.var_dipendente.set(nome_completo)
        self.var_mese_anno.set(f"{mese_nome} {dati['anno']}")
        self.var_importo.set(f"\u20ac {importo_in_cifre(dati['net_paye'])}")
        self.var_lettere.set(importo_in_lettere(dati['net_paye']))

        self.data_pagamento = calcola_data_pagamento(dati["anno"], dati["mese"])
        self.var_data_pagamento.set(formatta_data_estesa(self.data_pagamento))

        self.entry_prot_anno.delete(0, "end")
        self.entry_prot_anno.insert(0, str(dati["anno"]))

        oggi = datetime.date.today()
        self.entry_prot_data.delete(0, "end")
        self.entry_prot_data.insert(0, formatta_data_protocollo(oggi))

        self.btn_genera.configure(state="normal", bg=COLOR_SUCCESS)

        self._log(f"Caricato PDF: {os.path.basename(filepath)}")
        self._log(f"Dipendente: {nome_completo}")
        self._log(f"Periodo: {mese_nome} {dati['anno']}")
        self._log(f"Importo netto: \u20ac {importo_in_cifre(dati['net_paye'])}")
        self._log(f"Data pagamento calcolata: {formatta_data_estesa(self.data_pagamento)}")

    def _valida_input(self) -> bool:
        prot_num = self.entry_prot_num.get().strip()
        if not prot_num:
            messagebox.showwarning("Attenzione", "Inserire il numero di protocollo.")
            return False
        if not prot_num.isdigit():
            messagebox.showwarning("Attenzione",
                                   "Il numero di protocollo deve essere numerico.")
            return False

        prot_anno = self.entry_prot_anno.get().strip()
        if not prot_anno or not prot_anno.isdigit() or len(prot_anno) != 4:
            messagebox.showwarning("Attenzione",
                                   "L'anno del protocollo deve essere di 4 cifre.")
            return False

        prot_data = self.entry_prot_data.get().strip()
        if not prot_data:
            messagebox.showwarning("Attenzione",
                                   "Inserire la data del protocollo.")
            return False
        try:
            datetime.datetime.strptime(prot_data, "%d/%m/%Y")
        except ValueError:
            messagebox.showwarning("Attenzione",
                                   "Data protocollo non valida. Formato: GG/MM/AAAA")
            return False

        data_override = self.entry_data_override.get().strip()
        if data_override:
            try:
                datetime.datetime.strptime(data_override, "%d/%m/%Y")
            except ValueError:
                messagebox.showwarning("Attenzione",
                                       "Data pagamento non valida. Formato: GG/MM/AAAA")
                return False

        return True

    def _genera_documenti(self):
        if not self.dati_pdf or not self.dati_dipendente:
            messagebox.showwarning("Attenzione",
                                   "Caricare prima un PDF cedolino.")
            return

        if not self._valida_input():
            return

        self.config = self.config_mgr.load_config()
        dati = self.dati_pdf
        dip = self.dati_dipendente
        mese = dati["mese"]
        anno = dati["anno"]
        cognome = dati["cognome"]
        net_paye = dati["net_paye"]

        data_override = self.entry_data_override.get().strip()
        if data_override:
            data_pag = datetime.datetime.strptime(data_override, "%d/%m/%Y").date()
            self._log(f"Data pagamento modificata manualmente: "
                      f"{formatta_data_estesa(data_pag)}")
        else:
            data_pag = self.data_pagamento

        prot_num_raw = self.entry_prot_num.get().strip()
        prot_anno = self.entry_prot_anno.get().strip()
        prot_num = f"{prot_num_raw}/{prot_anno}"
        prot_data = self.entry_prot_data.get().strip()

        mese_italiano = MESI_ITALIANO[mese - 1]
        mese_francese = MESI_FRANCESE[mese - 1]

        os.makedirs(APP_DIR + "/output", exist_ok=True)

        dati_pag = {
            "prot_num": prot_num,
            "prot_data": prot_data,
            "nome_oggetto": dip["nome_oggetto"],
            "mese_italiano": f"{mese_italiano} {anno}",
            "beneficiario": dip["beneficiario"],
            "indirizzo": dip["indirizzo"],
            "importo_completo": formatta_importo_pagamento(net_paye),
            "iban": dip["iban"],
            "swift": dip["swift"],
            "banca": dip["banca"],
            "data_valuta": formatta_data_italiana(data_pag),
        }

        nome_pag = costruisci_nome_file_pagamento(cognome, mese, anno)
        path_pag = os.path.join(APP_DIR, "output", nome_pag)
        template_pag = os.path.join(APP_DIR, "templates", "template_pagamento.docx")

        genera_pagamento(template_pag, path_pag, dati_pag)
        self.ultimo_path_pag = path_pag
        self._log(f"Generato: {nome_pag}")

        causale = (f"{self.config['societa_completa']} \u2013 "
                   f"Bulletin de Salaire {mese_francese} {anno}")

        dati_mese = {
            "beneficiario": dip["beneficiario"],
            "indirizzo": dip["indirizzo"],
            "iban": dip["iban"],
            "swift": dip["swift"],
            "banca": dip["banca"],
            "importo_mese": formatta_importo_mese(net_paye),
            "causale": causale,
        }

        nome_mese = costruisci_nome_file_mese(cognome, mese, anno)
        path_mese = os.path.join(APP_DIR, "output", nome_mese)
        template_mese = os.path.join(APP_DIR, "templates", "template_mese.docx")

        genera_mese(template_mese, path_mese, dati_mese)
        self.ultimo_path_mese = path_mese
        self._log(f"Generato: {nome_mese}")

        # Aggiorna UI documenti generati
        self.var_doc_pag.set(nome_pag)
        self.var_doc_mese.set(nome_mese)
        self.card_docs.grid()
        self.btn_apri_pag.configure(state="normal")
        self.btn_apri_mese.configure(state="normal")

        self._log("Generazione completata con successo!")
        messagebox.showinfo(
            "Completato",
            f"Documenti generati:\n\n"
            f"1. {nome_pag}\n"
            f"2. {nome_mese}\n\n"
            f"Cartella: {APP_DIR}/output",
        )

    def _apri_cartella(self):
        output_dir = os.path.join(APP_DIR, "output")
        os.makedirs(output_dir, exist_ok=True)
        subprocess.Popen(["explorer", os.path.normpath(output_dir)])

    def _apri_ultimo_pagamento(self):
        if self.ultimo_path_pag and os.path.exists(self.ultimo_path_pag):
            os.startfile(self.ultimo_path_pag)
        else:
            messagebox.showwarning("Attenzione", "Nessun documento Pagamento trovato.")

    def _apri_ultimo_mese(self):
        if self.ultimo_path_mese and os.path.exists(self.ultimo_path_mese):
            os.startfile(self.ultimo_path_mese)
        else:
            messagebox.showwarning("Attenzione", "Nessun documento Mese trovato.")


def main():
    root = tk.Tk()
    root.configure(bg=COLOR_BG)
    app = CedFRAApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
