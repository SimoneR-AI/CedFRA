"""Modulo per la conversione degli importi in cifre e lettere italiane."""

import re

from num2words import num2words


def importo_in_cifre(valore: float) -> str:
    """Converte un float in formato italiano: 5.091,21

    Usa il punto come separatore migliaia e la virgola per i decimali.
    """
    valore = round(valore, 2)
    parte_intera = int(valore)
    centesimi = round((valore - parte_intera) * 100)
    parte_intera_str = f"{parte_intera:,}".replace(",", ".")
    return f"{parte_intera_str},{centesimi:02d}"


def _spazia_lettere_italiane(testo: str) -> str:
    """Inserisce spazi nelle parole numeriche italiane generate da num2words.

    num2words produce tutto attaccato (es. 'seimilatrecentotrentacinque'),
    ma i documenti originali usano spazi tra i blocchi logici
    (es. 'seimila trecento trentacinque').
    """
    # Spazio dopo "mila" (se non è fine stringa)
    testo = re.sub(r"mila(?!$)", "mila ", testo)
    # Spazio dopo "cento" (se non è fine stringa)
    testo = re.sub(r"cento(?!$)", "cento ", testo)
    return testo


def importo_in_lettere(valore: float) -> str:
    """Converte un float in lettere italiane: cinquemila novantuno/21

    La parte intera viene convertita in parole italiane con spazi
    tra i blocchi logici, seguita da / e i centesimi in cifre.
    """
    valore = round(valore, 2)
    parte_intera = int(valore)
    centesimi = round((valore - parte_intera) * 100)
    lettere = num2words(parte_intera, lang="it")
    lettere = _spazia_lettere_italiane(lettere)
    return f"{lettere}/{centesimi:02d}"


def formatta_importo_pagamento(valore: float) -> str:
    """Formato completo per il documento Pagamento.

    Esempio: € 5.091,21 (cinquemila novantuno/21)
    """
    cifre = importo_in_cifre(valore)
    lettere = importo_in_lettere(valore)
    return f"\u20ac {cifre} ({lettere})"


def formatta_importo_mese(valore: float) -> str:
    """Formato per il documento Mese Anno.

    Esempio: € 5.091,21
    """
    cifre = importo_in_cifre(valore)
    return f"\u20ac {cifre}"
