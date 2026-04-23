"""Test per word_generator (nomi file)."""

from word_generator import costruisci_nome_file_mese, costruisci_nome_file_pagamento


class TestCostruisciNomeFilePagamento:
    def test_base(self):
        nome = costruisci_nome_file_pagamento("MARCHETTO", 3, 2026)
        assert nome == "202603_MARCHETTO_Pagamento_MAR26.docx"

    def test_gennaio(self):
        nome = costruisci_nome_file_pagamento("ROSSI", 1, 2025)
        assert nome == "202501_ROSSI_Pagamento_GEN25.docx"


class TestCostruisciNomeFileMese:
    def test_base(self):
        nome = costruisci_nome_file_mese("MARCHETTO", 3, 2026)
        assert nome == "202603_MARCHETTO_MARZO 2026.docx"
