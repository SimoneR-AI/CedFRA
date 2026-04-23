"""Modulo per il calcolo delle date di pagamento."""

import calendar
import datetime
import json
import os

import holidays


def _load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Festività italiane
_IT_HOLIDAYS = holidays.Italy()

CONFIG = _load_config()


def is_giorno_lavorativo(data: datetime.date) -> bool:
    """Restituisce True se la data è un giorno lavorativo (no weekend, no festività IT)."""
    if data.weekday() >= 5:  # Sabato=5, Domenica=6
        return False
    if data in _IT_HOLIDAYS:
        return False
    return True


def calcola_data_pagamento(anno: int, mese: int) -> datetime.date:
    """Calcola il terzultimo giorno lavorativo del mese.

    Parte dall'ultimo giorno del mese e conta a ritroso
    i giorni lavorativi (esclusi sabato, domenica e festività
    nazionali italiane). Restituisce il terzo giorno lavorativo
    contando dalla fine.
    """
    ultimo_giorno = calendar.monthrange(anno, mese)[1]
    data = datetime.date(anno, mese, ultimo_giorno)

    giorni_lav_trovati = 0
    while giorni_lav_trovati < 3:
        if is_giorno_lavorativo(data):
            giorni_lav_trovati += 1
        if giorni_lav_trovati < 3:
            data -= datetime.timedelta(days=1)

    return data


def formatta_data_italiana(data: datetime.date) -> str:
    """Formatta una data come '27 marzo 2026'."""
    mese_nome = CONFIG["mesi_italiano"][data.month - 1]
    return f"{data.day} {mese_nome} {data.year}"


def formatta_data_estesa(data: datetime.date) -> str:
    """Formatta una data come 'Venerdì 27/03/2026'."""
    giorno_nome = CONFIG["giorni_settimana"][data.weekday()]
    return f"{giorno_nome} {data.strftime('%d/%m/%Y')}"


def formatta_data_protocollo(data: datetime.date) -> str:
    """Formatta una data come 'DD/MM/YYYY'."""
    return data.strftime("%d/%m/%Y")
