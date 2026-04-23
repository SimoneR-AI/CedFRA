"""Pannello configurazione Toplevel con tab Dipendenti, Società, Storico."""

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# Colori brand (duplicati qui per indipendenza, possono essere importati)
BRAND_NAVY = "#1C3D71"
BRAND_NAVY_LIGHT = "#2A5298"
BRAND_GOLD = "#C8A864"
COLOR_WHITE = "#FFFFFF"
COLOR_CARD = "#FFFFFF"
COLOR_TEXT = "#1E1E1E"
COLOR_TEXT_MUTED = "#6B7280"
COLOR_BORDER = "#D1D5DB"
COLOR_SUCCESS = "#16A34A"
COLOR_DANGER = "#DC2626"


class ConfigPanel:
    """Finestra di configurazione con CRUD dipendenti, società e storico."""

    def __init__(self, parent, config_mgr, log_callback=None):
        self.parent = parent
        self.config_mgr = config_mgr
        self.log = log_callback or (lambda msg: None)
        self.config = self.config_mgr.load_config()

        self.window = tk.Toplevel(parent)
        self.window.title("CedFRA — Configurazione")
        self.window.geometry("750x600")
        self.window.configure(bg=COLOR_CARD)
        self.window.transient(parent)

        self._build_header()
        self._build_notebook()
        self._build_actions()
        self._refresh_all()
        self.log("Finestra configurazione aperta")

    def _build_header(self):
        hdr = tk.Frame(self.window, bg=BRAND_NAVY, height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="Configurazione", font=("Segoe UI Semibold", 13),
                 bg=BRAND_NAVY, fg=COLOR_WHITE).pack(side="left", padx=16, pady=12)
        tk.Button(hdr, text="X", font=("Segoe UI", 10), bg=BRAND_NAVY, fg=COLOR_WHITE,
                  relief="flat", cursor="hand2", command=self.close,
                  width=3).pack(side="right", padx=8, pady=8)

    def _styled_button(self, parent, text, command, bg=BRAND_NAVY, fg=COLOR_WHITE,
                       font=("Segoe UI Semibold", 10), **kw):
        btn = tk.Button(parent, text=text, font=font, bg=bg, fg=fg,
                        activebackground=BRAND_NAVY_LIGHT, activeforeground=COLOR_WHITE,
                        relief="flat", cursor="hand2", command=command, **kw)
        return btn

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self._build_tab_dipendenti()
        self._build_tab_societa()
        self._build_tab_storico()

    def _build_actions(self):
        btn_frame = tk.Frame(self.window, bg=COLOR_CARD)
        btn_frame.pack(fill="x", padx=8, pady=(0, 8))
        self._styled_button(btn_frame, text="Esporta Config",
                            command=self._export_config, bg=BRAND_NAVY,
                            font=("Segoe UI", 9), padx=8, pady=4).pack(side="left", padx=(0, 4))
        self._styled_button(btn_frame, text="Importa Config",
                            command=self._import_config, bg=BRAND_NAVY,
                            font=("Segoe UI", 9), padx=8, pady=4).pack(side="left", padx=(0, 4))
        self._styled_button(btn_frame, text="Ricarica",
                            command=self._reload_config, bg=COLOR_BORDER,
                            font=("Segoe UI", 9), padx=8, pady=4).pack(side="right")

    # ── Tab Dipendenti ───────────────────────────────────────────────

    def _build_tab_dipendenti(self):
        tab = tk.Frame(self.notebook, bg=COLOR_CARD)
        self.notebook.add(tab, text="  Dipendenti  ")

        # Treeview
        tree_frame = tk.Frame(tab, bg=COLOR_CARD)
        tree_frame.pack(fill="x", pady=(8, 4))

        columns = ("cognome", "nome", "banca", "iban")
        self.tree_dip = ttk.Treeview(tree_frame, columns=columns, show="headings", height=6)
        for col, title, width in (("cognome", "Cognome", 100),
                                   ("nome", "Nome", 80),
                                   ("banca", "Banca", 120),
                                   ("iban", "IBAN", 140)):
            self.tree_dip.heading(col, text=title)
            self.tree_dip.column(col, width=width)
        self.tree_dip.pack(side="left", fill="x", expand=True)
        self.tree_dip.bind("<<TreeviewSelect>>", self._on_dip_select)

        sb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree_dip.yview)
        sb.pack(side="right", fill="y")
        self.tree_dip.configure(yscrollcommand=sb.set)

        # Pulsanti lista
        btn_row = tk.Frame(tab, bg=COLOR_CARD)
        btn_row.pack(fill="x", pady=(4, 8))
        self._styled_button(btn_row, text="+ Aggiungi", command=self._add_dipendente,
                            bg=COLOR_SUCCESS, font=("Segoe UI", 9), padx=8, pady=4).pack(side="left")
        self.btn_delete_dip = self._styled_button(
            btn_row, text="Elimina", command=self._delete_dipendente,
            bg=COLOR_DANGER, font=("Segoe UI", 9), padx=8, pady=4)
        self.btn_delete_dip.pack(side="left", padx=(4, 0))
        self.btn_restore_dip = self._styled_button(
            btn_row, text="Ripristina", command=self._restore_dipendente,
            bg=COLOR_SUCCESS, font=("Segoe UI", 9), padx=8, pady=4)
        self.btn_restore_dip.pack(side="left", padx=(4, 0))
        self.btn_restore_dip.configure(state="disabled")
        self._styled_button(btn_row, text="Mostra inattivi", command=self._toggle_inattivi,
                            bg=COLOR_BORDER, font=("Segoe UI", 9), padx=8, pady=4).pack(side="right")

        # Form dettaglio
        form_frame = tk.Frame(tab, bg=COLOR_CARD, highlightbackground=COLOR_BORDER,
                              highlightthickness=1, padx=12, pady=8)
        form_frame.pack(fill="both", expand=True)

        tk.Label(form_frame, text="Dettaglio Dipendente", font=("Segoe UI Semibold", 10),
                 bg=COLOR_CARD, fg=BRAND_NAVY).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        self.dip_fields = {}
        dip_labels = [
            ("cognome", "Cognome (chiave):"),
            ("nome", "Nome:"),
            ("nome_oggetto", "Nome oggetto:"),
            ("beneficiario", "Beneficiario:"),
            ("indirizzo", "Indirizzo:"),
            ("iban", "IBAN:"),
            ("swift", "SWIFT:"),
            ("banca", "Banca:"),
        ]
        for i, (field, label) in enumerate(dip_labels, 1):
            tk.Label(form_frame, text=label, font=("Segoe UI", 9),
                     bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, anchor="e").grid(
                row=i, column=0, sticky="e", padx=(0, 8), pady=2)
            var = tk.StringVar()
            entry = tk.Entry(form_frame, textvariable=var, font=("Segoe UI", 9),
                             relief="solid", bd=1, highlightcolor=BRAND_NAVY, highlightthickness=1)
            entry.grid(row=i, column=1, sticky="ew", pady=2)
            self.dip_fields[field] = var
            form_frame.grid_columnconfigure(1, weight=1)

        # Pulsanti form
        form_btns = tk.Frame(form_frame, bg=COLOR_CARD)
        form_btns.grid(row=len(dip_labels) + 1, column=0, columnspan=2, pady=(12, 0))
        self._styled_button(form_btns, text="Salva", command=self._save_dipendente,
                            bg=COLOR_SUCCESS, font=("Segoe UI Semibold", 9),
                            padx=16, pady=6).pack(side="left", padx=(0, 8))
        self._styled_button(form_btns, text="Annulla", command=self._cancel_dipendente,
                            bg=COLOR_BORDER, font=("Segoe UI", 9),
                            padx=16, pady=6).pack(side="left")

        self.selected_dip_key = None
        self.show_inattivi = False

    def _refresh_dipendenti_list(self):
        for item in self.tree_dip.get_children():
            self.tree_dip.delete(item)
        dipendenti = self.config.get("dipendenti", {})
        for key, data in sorted(dipendenti.items()):
            if not self.show_inattivi and not data.get("attivo", True):
                continue
            iban = data.get("iban", "")
            iban_masked = iban[:6] + "****" + iban[-4:] if len(iban) > 10 else iban
            self.tree_dip.insert("", "end", iid=key, values=(
                key, data.get("nome", ""), data.get("banca", ""), iban_masked,
            ))

    def _on_dip_select(self, event=None):
        selected = self.tree_dip.selection()
        if not selected:
            return
        key = selected[0]
        self.selected_dip_key = key
        data = self.config["dipendenti"].get(key, {})
        for field, var in self.dip_fields.items():
            var.set(data.get(field, ""))

        is_attivo = data.get("attivo", True)
        self.btn_delete_dip.configure(state="normal" if is_attivo else "disabled")
        self.btn_restore_dip.configure(state="disabled" if is_attivo else "normal")

    def _save_dipendente(self):
        if not self.selected_dip_key:
            messagebox.showwarning("Attenzione", "Seleziona un dipendente dalla lista.")
            return
        key = self.selected_dip_key
        updates = {}
        for field, var in self.dip_fields.items():
            val = var.get().strip()
            if field == "iban" and val and not self.config_mgr.validate_iban(val):
                messagebox.showerror("Errore", f"IBAN non valido: {val}")
                return
            if field == "swift" and val and not self.config_mgr.validate_swift(val):
                messagebox.showerror("Errore", f"SWIFT non valido: {val}")
                return
            updates[field] = val
        try:
            self.config_mgr.update_dipendente_multi(key, updates)
            self.config = self.config_mgr.load_config()
            self._refresh_dipendenti_list()
            self.log(f"Dipendente '{key}' aggiornato")
            messagebox.showinfo("Salvato", f"Dipendente '{key}' aggiornato con successo.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def _cancel_dipendente(self):
        if self.selected_dip_key:
            data = self.config["dipendenti"].get(self.selected_dip_key, {})
            for field, var in self.dip_fields.items():
                var.set(data.get(field, ""))

    def _add_dipendente(self):
        dialog = tk.Toplevel(self.parent)
        dialog.title("Aggiungi Dipendente")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        dialog.grab_set()

        tk.Label(dialog, text="Chiave (COGNOME):", font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(16, 4))
        key_var = tk.StringVar()
        tk.Entry(dialog, textvariable=key_var, font=("Segoe UI", 9)).pack(fill="x", padx=16)

        tk.Label(dialog, text="Nome:", font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(12, 4))
        nome_var = tk.StringVar()
        tk.Entry(dialog, textvariable=nome_var, font=("Segoe UI", 9)).pack(fill="x", padx=16)

        tk.Label(dialog, text="Banca:", font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(12, 4))
        banca_var = tk.StringVar()
        tk.Entry(dialog, textvariable=banca_var, font=("Segoe UI", 9)).pack(fill="x", padx=16)

        def on_confirm():
            key = key_var.get().strip().upper()
            if not key:
                messagebox.showwarning("Attenzione", "Inserire la chiave (cognome).")
                return
            data = {
                "nome": nome_var.get().strip(),
                "cognome": key,
                "nome_oggetto": nome_var.get().strip() + " " + key,
                "beneficiario": key + " " + nome_var.get().strip(),
                "indirizzo": "",
                "iban": "",
                "swift": "",
                "banca": banca_var.get().strip(),
            }
            try:
                self.config_mgr.add_dipendente(key, data)
                self.config = self.config_mgr.load_config()
                self._refresh_dipendenti_list()
                self.log(f"Nuovo dipendente '{key}' aggiunto")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Errore", str(e))

        btn_frame = tk.Frame(dialog, bg=COLOR_CARD)
        btn_frame.pack(fill="x", padx=16, pady=16)
        self._styled_button(btn_frame, text="Aggiungi", command=on_confirm,
                            bg=COLOR_SUCCESS, font=("Segoe UI", 9), padx=16, pady=6).pack(side="left")
        self._styled_button(btn_frame, text="Annulla", command=dialog.destroy,
                            bg=COLOR_BORDER, font=("Segoe UI", 9), padx=16, pady=6).pack(side="right")

    def _delete_dipendente(self):
        if not self.selected_dip_key:
            messagebox.showwarning("Attenzione", "Seleziona un dipendente.")
            return
        if messagebox.askyesno("Conferma", f"Disattivare il dipendente '{self.selected_dip_key}'?"):
            try:
                self.config_mgr.delete_dipendente(self.selected_dip_key)
                self.config = self.config_mgr.load_config()
                self._refresh_dipendenti_list()
                self.log(f"Dipendente '{self.selected_dip_key}' disattivato")
                self.selected_dip_key = None
                for var in self.dip_fields.values():
                    var.set("")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    def _restore_dipendente(self):
        if not self.selected_dip_key:
            messagebox.showwarning("Attenzione", "Seleziona un dipendente.")
            return
        if messagebox.askyesno("Conferma", f"Riattivare il dipendente '{self.selected_dip_key}'?"):
            try:
                self.config_mgr.restore_dipendente(self.selected_dip_key)
                self.config = self.config_mgr.load_config()
                self._refresh_dipendenti_list()
                self.log(f"Dipendente '{self.selected_dip_key}' ripristinato")
                messagebox.showinfo("Ripristinato", f"Dipendente '{self.selected_dip_key}' ripristinato.")
                self.selected_dip_key = None
                for var in self.dip_fields.values():
                    var.set("")
            except Exception as e:
                messagebox.showerror("Errore", str(e))

    def _toggle_inattivi(self):
        self.show_inattivi = not self.show_inattivi
        if self.show_inattivi:
            self.btn_restore_dip.configure(state="normal")
        else:
            self.btn_restore_dip.configure(state="disabled")
        self._refresh_dipendenti_list()

    # ── Tab Società ──────────────────────────────────────────────────

    def _build_tab_societa(self):
        tab = tk.Frame(self.notebook, bg=COLOR_CARD)
        self.notebook.add(tab, text="  Società  ")

        form_frame = tk.Frame(tab, bg=COLOR_CARD, padx=12, pady=8)
        form_frame.pack(fill="both", expand=True)

        self.soc_fields = {}
        soc_labels = [
            ("societa", "Società:"),
            ("societa_completa", "Società completa:"),
            ("firmatario", "Firmatario:"),
            ("mittente", "Mittente:"),
            ("destinatari", "Destinatari:"),
            ("cc", "Cc:"),
            ("causale_pagamento", "Causale pagamento:"),
            ("oggetto_prefisso", "Oggetto prefisso:"),
        ]
        for i, (field, label) in enumerate(soc_labels):
            tk.Label(form_frame, text=label, font=("Segoe UI", 9),
                     bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, anchor="e").grid(
                row=i, column=0, sticky="e", padx=(0, 8), pady=4)
            var = tk.StringVar()
            entry = tk.Entry(form_frame, textvariable=var, font=("Segoe UI", 9),
                             relief="solid", bd=1, highlightcolor=BRAND_NAVY, highlightthickness=1)
            entry.grid(row=i, column=1, sticky="ew", pady=4)
            self.soc_fields[field] = var
            form_frame.grid_columnconfigure(1, weight=1)

        btn_frame = tk.Frame(form_frame, bg=COLOR_CARD)
        btn_frame.grid(row=len(soc_labels), column=0, columnspan=2, pady=(12, 0))
        self._styled_button(btn_frame, text="Salva", command=self._save_societa,
                            bg=COLOR_SUCCESS, font=("Segoe UI Semibold", 9),
                            padx=16, pady=6).pack(side="left")

    def _refresh_societa_form(self):
        for field, var in self.soc_fields.items():
            var.set(self.config.get(field, ""))

    def _save_societa(self):
        updates = {field: var.get().strip() for field, var in self.soc_fields.items()}
        try:
            self.config_mgr.update_societa(updates)
            self.config = self.config_mgr.load_config()
            self.log("Configurazione società aggiornata")
            messagebox.showinfo("Salvato", "Configurazione società aggiornata.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    # ── Tab Storico ──────────────────────────────────────────────────

    def _build_tab_storico(self):
        tab = tk.Frame(self.notebook, bg=COLOR_CARD)
        self.notebook.add(tab, text="  Storico  ")

        # Info backup
        backup_frame = tk.Frame(tab, bg=COLOR_CARD, padx=8, pady=8)
        backup_frame.pack(fill="x", pady=(0, 4))
        self.lbl_backup_info = tk.Label(
            backup_frame, text="", font=("Segoe UI", 9),
            bg=COLOR_CARD, fg=COLOR_TEXT_MUTED, anchor="w",
        )
        self.lbl_backup_info.pack(side="left", fill="x", expand=True)
        self._styled_button(
            backup_frame, text="Pulisci vecchi backup",
            command=self._cleanup_backups_manual,
            bg=COLOR_BORDER, font=("Segoe UI", 9), padx=8, pady=4,
        ).pack(side="right")

        self.tree_storico = ttk.Treeview(tab, columns=("ts", "action", "entity", "field", "old", "new"),
                                          show="headings", height=15)
        for col, title, width in (("ts", "Timestamp", 140),
                                   ("action", "Azione", 70),
                                   ("entity", "Entità", 80),
                                   ("field", "Campo", 80),
                                   ("old", "Vecchio", 120),
                                   ("new", "Nuovo", 120)):
            self.tree_storico.heading(col, text=title)
            self.tree_storico.column(col, width=width)

        sb = ttk.Scrollbar(tab, orient="vertical", command=self.tree_storico.yview)
        self.tree_storico.configure(yscrollcommand=sb.set)
        self.tree_storico.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _refresh_storico(self):
        for item in self.tree_storico.get_children():
            self.tree_storico.delete(item)
        history = self.config_mgr.get_history(limit=100)
        for entry in reversed(history):
            ts = entry.get("ts", "")[:19].replace("T", " ")
            old = str(entry.get("old", ""))[:50]
            new = str(entry.get("new", ""))[:50]
            self.tree_storico.insert("", "end", values=(
                ts, entry.get("action", ""), entry.get("entity", ""),
                entry.get("field", ""), old, new,
            ))

    def _refresh_backup_info(self):
        count = len(self.config_mgr.list_backups())
        self.lbl_backup_info.configure(
            text=f"Backup automatici: {count} file conservati (max 30)"
        )

    def _cleanup_backups_manual(self):
        try:
            self.config_mgr._cleanup_old_backups(keep=30)
            self._refresh_backup_info()
            self.log("Pulizia backup vecchi completata")
            messagebox.showinfo("Completato", "Backup vecchi rimossi.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    # ── Azioni globali ───────────────────────────────────────────────

    def _export_config(self):
        filepath = filedialog.asksaveasfilename(
            title="Esporta configurazione", defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            initialdir=os.path.dirname(self.config_mgr.app_dir),
        )
        if not filepath:
            return
        try:
            self.config_mgr.export_config(filepath)
            self.log(f"Configurazione esportata: {os.path.basename(filepath)}")
            messagebox.showinfo("Esportato", f"Configurazione esportata in:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def _import_config(self):
        filepath = filedialog.askopenfilename(
            title="Importa configurazione", filetypes=[("JSON files", "*.json")],
            initialdir=os.path.dirname(self.config_mgr.app_dir),
        )
        if not filepath:
            return
        if not messagebox.askyesno("Conferma", "Importare questa configurazione?\nVerrà creato un backup automatico."):
            return
        try:
            self.config_mgr.import_config(filepath)
            self.config = self.config_mgr.load_config()
            self._refresh_all()
            self.log(f"Configurazione importata: {os.path.basename(filepath)}")
            messagebox.showinfo("Importato", "Configurazione importata con successo.")
        except Exception as e:
            messagebox.showerror("Errore", str(e))

    def _reload_config(self):
        self.config = self.config_mgr.load_config()
        self._refresh_all()
        self.log("Configurazione ricaricata")

    def _refresh_all(self):
        self._refresh_dipendenti_list()
        if hasattr(self, "soc_fields"):
            self._refresh_societa_form()
        if hasattr(self, "tree_storico"):
            self._refresh_storico()
        if hasattr(self, "lbl_backup_info"):
            self._refresh_backup_info()

    def close(self):
        self.window.destroy()
        self.log("Finestra configurazione chiusa")

    def is_open(self):
        return self.window.winfo_exists()
