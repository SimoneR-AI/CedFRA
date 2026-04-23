"""Test per date_utils."""

import datetime

import pytest

from date_utils import (
    calcola_data_pagamento,
    formatta_data_estesa,
    formatta_data_italiana,
    is_giorno_lavorativo,
)


class TestIsGiornoLavorativo:
    def test_lunedi(self):
        d = datetime.date(2026, 4, 20)  # lunedì
        assert is_giorno_lavorativo(d) is True

    def test_sabato(self):
        d = datetime.date(2026, 4, 18)  # sabato
        assert is_giorno_lavorativo(d) is False

    def test_domenica(self):
        d = datetime.date(2026, 4, 19)  # domenica
        assert is_giorno_lavorativo(d) is False

    def test_festa_nazionale(self):
        d = datetime.date(2026, 6, 2)  # festa della Repubblica
        assert is_giorno_lavorativo(d) is False


class TestCalcolaDataPagamento:
    def test_marzo_2026(self):
        # marzo 2026: ultimo giorno 31 (martedì)
        # giorni lavorativi a ritroso: 31, 30, 27 (venerdì)
        d = calcola_data_pagamento(2026, 3)
        assert d == datetime.date(2026, 3, 27)

    def test_aprile_2026(self):
        # aprile 2026: ultimo giorno 30 (giovedì)
        # giorni lavorativi a ritroso: 30, 29, 28
        d = calcola_data_pagamento(2026, 4)
        assert d == datetime.date(2026, 4, 28)


class TestFormattaDataItaliana:
    def test_base(self):
        d = datetime.date(2026, 3, 27)
        assert formatta_data_italiana(d) == "27 marzo 2026"


class TestFormattaDataEstesa:
    def test_base(self):
        d = datetime.date(2026, 3, 27)  # venerdì
        assert formatta_data_estesa(d) == "Venerdì 27/03/2026"
