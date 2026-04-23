# CedFRA - Istruzioni OpenCode

## Project Overview
- **App**: CedFRA - Generatore Documenti Retribuzioni
- **Versione**: 1.2.2
- **Framework**: Tkinter (Python)
- **Path**: `app/`
- **Entry**: `Avvia_CedFRA.bat` → `app/app.py`

## Dipendenti
- **JOUNEAU LUDWIG** - Francia (BoursoBank)
- **MARCHETTO REDI** - Italia (Credem)

## Architettura moduli (post-refactor v1.2.2)
- `app/app.py` — Entry point UI principale (main panel, logica workflow)
- `app/ui/config_panel.py` — Finestra configurazione Toplevel (tab Dipendenti, Società, Storico)
- `app/config_manager.py` — CRUD config, backup, storico, validazione IBAN/SWIFT
- `app/pdf_extractor.py` — Estrazione dati da PDF cedolino
- `app/word_generator.py` — Generazione documenti Word da template
- `app/amount_converter.py` — Conversione importi in cifre/lettere (Decimal)
- `app/date_utils.py` — Calcolo date pagamento e formattazione
- `app/constants.py` — Costanti statiche (mesi, giorni della settimana)

## Configurazione
- `app/config.json` — Dati dinamici: dipendenti, società (NO più mesi/giorni statici)
- `app/config_manager.py` — Modulo gestione config con CRUD, backup, storico
- `app/changelog.json` — Changelog strutturato
- `app/config_history.jsonl` — Log append-only modifiche config
- `app/backups/` — Backup automatici config
- `app/logs/` — Log operazioni giornalieri (cedfra_YYYY-MM-DD.log)

## File Naming
- Pagamento: `YYYYMM_COGNOME_Pagamento_MESYY.docx`
- Mese: `YYYYMM_COGNOME_MESE AAAA.docx`

## Workflow Mensile
1. Carica PDF cedolino
2. Inserisci numero protocollo
3. Genera documenti (Pagamento + Mese)
4. Output in `app/output/`

## Configurazione UI (v1.2)
- Pannello configurazione toggle con pulsante ⚙ (apre ConfigPanel Toplevel)
- Tab: Dipendenti, Società, Storico
- CRUD dipendenti con validazione IBAN (modulo 97) / SWIFT
- Soft-delete dipendenti con pulsante "Ripristina" in modalità inattivi
- Export/Import config JSON con validazione schema
- Backup automatico prima di ogni modifica (rotazione: ultimi 30)
- Pulsanti "Apri Pagamento" / "Apri Mese" dopo generazione documenti

## Validazioni implementate
- **IBAN**: regex + algoritmo modulo 97 (ISO 13616)
- **SWIFT**: regex formato standard
- **Config import**: validazione schema tipizzata (dipendenti dict, attivo bool, ecc.)
- **Importi**: uso di `Decimal` per evitare errori di arrotondamento float

## Istruzioni per LLM
- Usa sempre `app/` come directory principale
- NON modificare `CedFRA/` (obsoleto, archiviato in OldVersions/)
- NON modificare `scratch/` (file sviluppo temporanei)
- Test: `python -m pytest app/tests -v`
- Avvio: `python app/app.py`

## Git Workflow — Push automatico
- **Repository remoto:** https://github.com/SimoneR-AI/CedFRA
- **Alla fine di ogni sessione di lavoro**, l'agent DEVE:
  1. Verificare se ci sono modifiche non committate (`git status`)
  2. Se sì, eseguire `git add .`, `git commit -m "<tipo>: <descrizione>"` e `git push origin main`
  3. Se il push fallisce per autenticazione, avvisare l'utente
- **Su richiesta esplicita dell'utente** (es. "salva su GitHub", "fai push", "commit e push"), eseguire immediatamente il workflow sopra
- Lo script `push_to_github.py` è disponibile per push rapido con messaggio auto-generato

## Risorse
- Templates: `app/templates/`
- Assets: `app/assets/`
- Reference: `OldVersions/CedFRA_v1/riferimenti/`

## Session Notes
- Vedi `SESSION_NOTES.md` per stato, problemi aperti e prossimi step
