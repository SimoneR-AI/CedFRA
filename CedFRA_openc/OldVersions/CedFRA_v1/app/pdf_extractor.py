"""Modulo per l'estrazione dei dati retributivi dai PDF dei cedolini."""

import re

import pdfplumber


def estrai_dati_cedolino(pdf_path: str) -> dict:
    """Estrae i dati principali da un PDF cedolino (Bulletin de Salaire).

    Ritorna un dizionario con:
        - cognome: str (es. "MARCHETTO")
        - nome: str (es. "Redi")
        - mese: int (1-12)
        - anno: int (es. 2026)
        - net_paye: float (es. 5091.21)

    Raises:
        ValueError: se il PDF non contiene i dati attesi.
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()

    if not text:
        raise ValueError(f"Impossibile estrarre testo dal PDF: {pdf_path}")

    lines = text.split("\n")

    # --- Riga header: MIS.P.A##BULLETIN##MM-YYYY##MATRICOLA##COGNOME##Nome##SIRET
    header_line = lines[0] if lines else ""
    header_match = re.match(
        r"MIS\.P\.A##BULLETIN##(\d{2})-(\d{4})##\d+##(\w+)##(\w+)##",
        header_line,
    )
    if not header_match:
        raise ValueError(
            f"Header del cedolino non riconosciuto: {header_line!r}"
        )

    mese = int(header_match.group(1))
    anno = int(header_match.group(2))
    cognome = header_match.group(3)
    nome = header_match.group(4)

    # --- Net payé: cerco la riga "Net payé : X XXX.XX euros"
    net_paye = None
    for line in lines:
        match = re.search(r"Net pay[eé]\s*:\s*([\d\s]+\.\d{2})\s*euros", line)
        if match:
            valore_str = match.group(1).replace(" ", "")
            net_paye = float(valore_str)
            break

    if net_paye is None:
        raise ValueError(f"Importo 'Net payé' non trovato nel PDF: {pdf_path}")

    return {
        "cognome": cognome,
        "nome": nome,
        "mese": mese,
        "anno": anno,
        "net_paye": net_paye,
    }
