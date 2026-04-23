# Guida Rapida Git — CedFRA

> Istruzioni semplici per aggiornare il progetto su GitHub quando fai modifiche.

---

## 1. Guarda cosa è cambiato

Dopo aver modificato file, apri il terminale nella cartella del progetto e scrivi:

```bash
git status
```

Ti mostra in rosso i file modificati e in verde quelli pronti per essere salvati.

---

## 2. Prepara i file da salvare ("stage")

Per aggiungere TUTTI i file modificati:

```bash
git add .
```

Oppure per aggiungere solo un file specifico:

```bash
git add app/app.py
```

---

## 3. Salva le modifiche ("commit")

Scrivi un messaggio che dica cosa hai fatto:

```bash
git commit -m "fix: corretto bug nel calcolo date"
```

**Regole per il messaggio:**
- Inizia con il tipo: `feat:` (nuova funzione), `fix:` (correzione), `docs:` (documentazione), `refactor:` (pulizia codice)
- Poi una breve descrizione in italiano

**Esempi:**
- `feat: aggiunto nuovo campo indirizzo`
- `fix: risolto errore validazione IBAN`
- `docs: aggiornato README`

---

## 4. Invia su GitHub ("push")

```bash
git push origin main
```

Ti chiederà:
- **Username:** `SimoneR-AI`
- **Password:** il tuo **Personal Access Token** (quello lungo che inizia con `ghp_`)

> Nota: quando incolli il token, non vedrai i caratteri (è normale per sicurezza). Premi Invio dopo aver incollato.

---

## 5. Workflow completo (esempio)

Supponiamo che hai modificato `app.py` e `config_panel.py`:

```bash
git status                          # vedi i file modificati
git add .                           # aggiungi tutto
git commit -m "feat: migliorata UI configurazione"
git push origin main              # invia su GitHub
```

---

## 6. Comandi utili extra

| Comando | Cosa fa |
|---------|---------|
| `git log --oneline -5` | Vedi gli ultimi 5 commit |
| `git diff` | Vedi le differenze nei file modificati |
| `git pull origin main` | Scarica eventuali modifiche dal repo remoto |

---

## 7. Se qualcosa va storto

**"Non riesco a pushare"**
- Verifica di essere nella cartella giusta (`CedFRA_openc`)
- Controlla che il token non sia scaduto (ne devi creare uno nuovo su GitHub)

**"Ho dimenticato di aggiungere un file al commit"**
```bash
git add nome_file.py
git commit --amend --no-edit
git push origin main --force-with-lease
```

**"Voglio annullare tutte le modifiche"**
```bash
git checkout -- .
```
⚠️ Attenzione: perde tutte le modifiche non committate!

---

## Link utili

- **Il tuo repository:** https://github.com/SimoneR-AI/CedFRA
- **Crea nuovo token:** https://github.com/settings/tokens

---

*Ultimo aggiornamento: 2026-04-23*
