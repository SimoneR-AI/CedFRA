"""Script per push automatico su GitHub.

Uso:
    python push_to_github.py
    python push_to_github.py "messaggio commit personalizzato"

Se non viene fornito un messaggio, usa la data/ora corrente.
"""

import datetime
import subprocess
import sys

def run(cmd, **kw):
    print(f">>> {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print(f"ERRORE: comando fallito con codice {result.returncode}")
        sys.exit(1)
    return result

def main():
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    else:
        msg = f"chore: auto-commit {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"

    print("=" * 50)
    print("CedFRA — Push automatico su GitHub")
    print("=" * 50)

    # 1. Status
    run(["git", "status", "--short"])

    # 2. Add
    run(["git", "add", "."])

    # 3. Commit
    run(["git", "commit", "-m", msg])

    # 4. Push
    run(["git", "push", "origin", "main"])

    print("\n✅ Push completato con successo!")
    print("🔗 https://github.com/SimoneR-AI/CedFRA")

if __name__ == "__main__":
    main()
