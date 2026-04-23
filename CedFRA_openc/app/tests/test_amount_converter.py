"""Test per amount_converter."""

import pytest

from amount_converter import (
    formatta_importo_mese,
    formatta_importo_pagamento,
    importo_in_cifre,
    importo_in_lettere,
)


class TestImportoInCifre:
    def test_base(self):
        assert importo_in_cifre(5091.21) == "5.091,21"

    def test_da_stringa(self):
        assert importo_in_cifre("5091.21") == "5.091,21"

    def test_arrotondamento_half_up(self):
        # 2.675 con Decimal half-up diventa 2,68
        assert importo_in_cifre(2.675) == "2,68"

    def test_centesimi_zero(self):
        assert importo_in_cifre(1000.00) == "1.000,00"

    def test_centesimi(self):
        assert importo_in_cifre(0.05) == "0,05"


class TestImportoInLettere:
    def test_base(self):
        assert importo_in_lettere(5091.21) == "cinquemila novantuno/21"

    def test_centesimi_zero(self):
        assert importo_in_lettere(1000.00) == "mille/00"


class TestFormattaImportoPagamento:
    def test_completo(self):
        ris = formatta_importo_pagamento(5091.21)
        assert ris == "\u20ac 5.091,21 (cinquemila novantuno/21)"


class TestFormattaImportoMese:
    def test_base(self):
        assert formatta_importo_mese(5091.21) == "\u20ac 5.091,21"
