"""Test per config_manager."""

import pytest

from config_manager import ConfigManager


class TestValidateIban:
    def test_iban_valido(self):
        assert ConfigManager.validate_iban("GB82WEST12345698765432") is True

    def test_iban_valido_con_spazi(self):
        assert ConfigManager.validate_iban("GB82 WEST 1234 5698 7654 32") is True

    def test_iban_errato_checksum(self):
        # cifra cambiata -> checksum fallisce
        assert ConfigManager.validate_iban("GB82WEST12345698765433") is False

    def test_iban_troppo_corto(self):
        assert ConfigManager.validate_iban("GB82") is False

    def test_iban_non_valido(self):
        assert ConfigManager.validate_iban("INVALID") is False


class TestValidateSwift:
    def test_swift_valido(self):
        assert ConfigManager.validate_swift("CCRTIT2TPRE") is True

    def test_swift_valido_con_spazi(self):
        assert ConfigManager.validate_swift("CCRT IT2T PRE") is True

    def test_swift_non_valido(self):
        assert ConfigManager.validate_swift("SHORT") is False


class TestValidateConfigSchema:
    def test_config_valido_minimo(self):
        cfg = {"dipendenti": {}}
        ConfigManager.validate_config_schema(cfg)

    def test_manca_dipendenti(self):
        with pytest.raises(ValueError, match="dipendenti"):
            ConfigManager.validate_config_schema({})

    def test_dipendenti_non_dict(self):
        with pytest.raises(ValueError, match="dipendenti"):
            ConfigManager.validate_config_schema({"dipendenti": []})

    def test_attivo_non_bool(self):
        with pytest.raises(ValueError, match="attivo"):
            ConfigManager.validate_config_schema(
                {"dipendenti": {"ROSSI": {"attivo": "sì"}}}
            )

    def test_campo_stringa_errato(self):
        with pytest.raises(ValueError, match="societa"):
            ConfigManager.validate_config_schema(
                {"dipendenti": {}, "societa": 123}
            )
