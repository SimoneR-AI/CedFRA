"""Modulo per la gestione della configurazione con storico e backup."""

import copy
import datetime
import json
import os
import re
import shutil


class ConfigManager:
    """Gestisce configurazione, backup, storico e CRUD dipendenti."""

    def __init__(self, app_dir: str):
        self.app_dir = app_dir
        self.config_path = os.path.join(app_dir, "config.json")
        self.history_path = os.path.join(app_dir, "config_history.jsonl")
        self.changelog_path = os.path.join(app_dir, "changelog.json")
        self.backups_dir = os.path.join(app_dir, "backups")
        os.makedirs(self.backups_dir, exist_ok=True)

    # ── Core ──────────────────────────────────────────────────────────

    def load_config(self) -> dict:
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_config(self, config: dict) -> None:
        self.backup_config()
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    def reload_config(self) -> dict:
        return self.load_config()

    # ── Backup ────────────────────────────────────────────────────────

    def backup_config(self) -> str:
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"config_backup_{ts}.json"
        backup_path = os.path.join(self.backups_dir, backup_name)
        shutil.copy2(self.config_path, backup_path)
        self.cleanup_old_backups()
        return backup_path

    def cleanup_old_backups(self, keep: int = 30) -> None:
        """Mantiene solo gli ultimi N backup, eliminando i più vecchi."""
        backups = self.list_backups()
        for old in backups[keep:]:
            try:
                os.remove(os.path.join(self.backups_dir, old))
            except OSError:
                pass

    def list_backups(self) -> list:
        if not os.path.exists(self.backups_dir):
            return []
        files = [f for f in os.listdir(self.backups_dir) if f.endswith(".json")]
        return sorted(files, reverse=True)

    def restore_backup(self, backup_name: str) -> None:
        backup_path = os.path.join(self.backups_dir, backup_name)
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup non trovato: {backup_name}")
        shutil.copy2(backup_path, self.config_path)
        self.log_change("restore", "config", "*", None, backup_name)

    # ── Storico ───────────────────────────────────────────────────────

    def log_change(self, action: str, entity: str, field: str, old, new) -> None:
        entry = {
            "ts": datetime.datetime.now().isoformat(),
            "action": action,
            "entity": entity,
            "field": field,
            "old": old,
            "new": new,
        }
        with open(self.history_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def get_history(self, limit: int = 100) -> list:
        if not os.path.exists(self.history_path):
            return []
        entries = []
        with open(self.history_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries[-limit:]

    # ── Validazione ───────────────────────────────────────────────────

    @staticmethod
    def validate_iban(iban: str) -> bool:
        """Valida un IBAN con regex di base + algoritmo modulo 97 (ISO 13616)."""
        iban_clean = iban.replace(" ", "")
        if not re.match(r"^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$", iban_clean):
            return False
        if len(iban_clean) < 15 or len(iban_clean) > 34:
            return False

        # Algoritmo modulo 97
        rearranged = iban_clean[4:] + iban_clean[:4]
        numeric = ""
        for ch in rearranged:
            if ch.isalpha():
                numeric += str(ord(ch.upper()) - ord("A") + 10)
            else:
                numeric += ch
        return int(numeric) % 97 == 1

    @staticmethod
    def validate_swift(swift: str) -> bool:
        swift_clean = swift.replace(" ", "")
        return bool(re.match(r"^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$", swift_clean))

    # ── Dipendenti CRUD ──────────────────────────────────────────────

    def get_dipendenti_attivi(self) -> dict:
        config = self.load_config()
        return {
            k: v for k, v in config.get("dipendenti", {}).items()
            if v.get("attivo", True)
        }

    def get_dipendente(self, key: str) -> dict | None:
        config = self.load_config()
        return config.get("dipendenti", {}).get(key)

    def add_dipendente(self, key: str, data: dict) -> None:
        config = self.load_config()
        key_upper = key.upper()
        if key_upper in config["dipendenti"]:
            raise ValueError(f"Dipendente '{key_upper}' già esistente")
        data["attivo"] = True
        config["dipendenti"][key_upper] = data
        self.save_config(config)
        self.log_change("add", key_upper, "*", None, data)

    def update_dipendente(self, key: str, field: str, value) -> None:
        config = self.load_config()
        if key not in config["dipendenti"]:
            raise ValueError(f"Dipendente '{key}' non trovato")
        old = config["dipendenti"][key].get(field)
        config["dipendenti"][key][field] = value
        self.save_config(config)
        self.log_change("modify", key, field, old, value)

    def update_dipendente_multi(self, key: str, updates: dict) -> None:
        config = self.load_config()
        if key not in config["dipendenti"]:
            raise ValueError(f"Dipendente '{key}' non trovato")
        old = {k: config["dipendenti"][key].get(k) for k in updates}
        config["dipendenti"][key].update(updates)
        self.save_config(config)
        for k, v in updates.items():
            self.log_change("modify", key, k, old.get(k), v)

    def delete_dipendente(self, key: str) -> None:
        config = self.load_config()
        if key not in config["dipendenti"]:
            raise ValueError(f"Dipendente '{key}' non trovato")
        old = config["dipendenti"][key].get("attivo", True)
        config["dipendenti"][key]["attivo"] = False
        self.save_config(config)
        self.log_change("delete", key, "attivo", old, False)

    def restore_dipendente(self, key: str) -> None:
        config = self.load_config()
        if key not in config["dipendenti"]:
            raise ValueError(f"Dipendente '{key}' non trovato")
        config["dipendenti"][key]["attivo"] = True
        self.save_config(config)
        self.log_change("restore", key, "attivo", False, True)

    # ── Società ───────────────────────────────────────────────────────

    def update_societa(self, updates: dict) -> None:
        config = self.load_config()
        old = {k: config.get(k) for k in updates}
        config.update(updates)
        self.save_config(config)
        for k, v in updates.items():
            self.log_change("modify", "societa", k, old.get(k), v)

    # ── Changelog ─────────────────────────────────────────────────────

    def get_changelog(self) -> list:
        if not os.path.exists(self.changelog_path):
            return []
        with open(self.changelog_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ── Export/Import ─────────────────────────────────────────────────

    def export_config(self, filepath: str) -> None:
        config = self.load_config()
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        self.log_change("export", "config", "*", None, filepath)

    @staticmethod
    def validate_config_schema(config: dict) -> None:
        """Valida la struttura minima di un file di configurazione.

        Raises:
            ValueError: se la struttura non è valida.
        """
        if not isinstance(config, dict):
            raise ValueError("Il file config deve contenere un oggetto JSON.")
        if "dipendenti" not in config:
            raise ValueError("File config non valido: manca 'dipendenti'.")
        if not isinstance(config["dipendenti"], dict):
            raise ValueError("'dipendenti' deve essere un oggetto (chiave: dati).")
        for key, data in config["dipendenti"].items():
            if not isinstance(data, dict):
                raise ValueError(f"Dipendente '{key}': i dati devono essere un oggetto.")
            if "attivo" in data and not isinstance(data["attivo"], bool):
                raise ValueError(f"Dipendente '{key}': 'attivo' deve essere true/false.")
        string_fields = ("societa", "societa_completa", "firmatario",
                         "mittente", "destinatari", "cc",
                         "causale_pagamento", "oggetto_prefisso")
        for field in string_fields:
            if field in config and not isinstance(config[field], str):
                raise ValueError(f"'{field}' deve essere una stringa.")

    def import_config(self, filepath: str) -> dict:
        with open(filepath, "r", encoding="utf-8") as f:
            imported = json.load(f)
        self.validate_config_schema(imported)
        old = self.load_config()
        self.save_config(imported)
        self.log_change("import", "config", "*", None, filepath)
        return imported
