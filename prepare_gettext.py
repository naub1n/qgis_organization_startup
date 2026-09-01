from pathlib import Path
import subprocess

files = [str(f) for f in Path("src").rglob("*.py")]

subprocess.run([
    "xgettext",
    "--language=Python",
    "--keyword=_tr",
    "--output=messages.pot",
    *files
], check=True)