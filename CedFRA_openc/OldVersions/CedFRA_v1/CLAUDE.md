# CedFRA

## Project Overview

Document management project containing monthly payroll and payment documents for:
- **JOUNEAU (LUDWIG)**
- **MARCHETTO (REDI)**

## File Naming Convention

- Payroll sheets: `YYYYMM_LASTNAME_MONTH-YY_new ci.docx`
- Payment slips: `YYYYMM_LASTNAME_Pagamento_MONTHYY.docx`
- PDF reports: `LASTNAME_FIRSTNAME_MM_YYYY_version.pdf`

## Notes

- Documents are in Italian
- Files cover monthly periods (currently January–March 2026)
- La data di pagamento delle retribuzioni è sempre il terzultimo giorno lavorativo del mese (esclusi sabato, domenica e festività nazionali italiane)

## Numeri di Protocollo

- Il numero di protocollo viene fornito dall'utente ogni mese
- Inserire sempre nei documenti di tipo "Pagamento": numero protocollo, descrizione, data protocollo e società
- Società: Marine Interiors

## Dipendenti

- MARCHETTO REDI (conto cointestato: Marchetto Redi - Cattai Valeria)
- JOUNEAU LUDWIG
- Entrambi dipendenti di Marine Interiors

## Workflow Mensile

- Partire sempre dall'analisi dei documenti Word dei mesi precedenti per replicarne struttura e formato
- Per ogni dipendente generare sempre 2 documenti:
  * Documento "Pagamento" → es. `202603_MARCHETTO_Pagamento_MAR26.docx`
  * Documento "Mese Anno" → es. `202603_MARCHETTO_MARZO 2026.docx`
- Estrarre i dati retributivi dai PDF dei cedolini paga
- Verificare la coerenza degli importi con i mesi precedenti
