from pathlib import Path
import subprocess
import shutil
import argparse

SOURCE_DIR = Path("src")
LOCALES_DIR = Path("src/qgis_organization_startup/locales")
DOMAIN = "messages"


def check_tool(name):
    if shutil.which(name) is None:
        raise RuntimeError(f"{name} introuvable dans le PATH")


def generate_pot():
    check_tool("xgettext")

    files = [str(f) for f in SOURCE_DIR.rglob("*.py")]

    if not files:
        raise RuntimeError("Aucun fichier Python trouvé")

    pot_file = LOCALES_DIR / f"{DOMAIN}.pot"

    subprocess.run(
        [
            "xgettext",
            "--language=Python",
            "--from-code=UTF-8",
            "--keyword=_tr",
            "--keyword=template_function:2",
            "-o",
            str(pot_file),
            *files,
        ],
        check=True,
    )

    return pot_file


def update_languages():
    check_tool("msgmerge")

    pot_file = generate_pot()

    for po_file in LOCALES_DIR.glob("*/LC_MESSAGES/*.po"):
        subprocess.run(
            [
                "msgmerge",
                "--update",
                "--backup=none",
                str(po_file),
                str(pot_file),
            ],
            check=True,
        )

        print(f"Updated: {po_file}")

        print(f"Vérification du fuzzy dans {po_file}:")

        subprocess.run(
            [
                "msgattrib",
                "--only-fuzzy",
                str(po_file)
            ],
            check=True,
        )


def init_language(lang):
    check_tool("msginit")

    pot_file = generate_pot()

    po_file = (
        LOCALES_DIR
        / lang
        / "LC_MESSAGES"
        / f"{DOMAIN}.po"
    )

    po_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    subprocess.run(
        [
            "msginit",
            "--no-translator",
            f"--locale={lang}",
            f"--input={pot_file}",
            f"--output-file={po_file}",
        ],
        check=True,
    )


def compile_mo():
    check_tool("msgfmt")

    for po_file in LOCALES_DIR.glob("*/LC_MESSAGES/*.po"):

        mo_file = po_file.with_suffix(".mo")

        subprocess.run(
            [
                "msgfmt",
                str(po_file),
                "-o",
                str(mo_file),
            ],
            check=True,
        )

        print(f"Compiled: {mo_file}")

def check():
    check_tool("msgfmt")

    for po_file in LOCALES_DIR.glob("*/LC_MESSAGES/*.po"):

        mo_file = po_file.with_suffix(".mo")

        subprocess.run(
            [
                "msgfmt",
                "--check",
                str(po_file),
                "-o",
                str(mo_file),
            ],
            check=True,
        )

        print(f"Checked: {mo_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--init",
        nargs="+",
        metavar="LANG",
        help="Initialiser une ou plusieurs langues"
    )

    parser.add_argument(
        "--update",
        action="store_true",
    )

    parser.add_argument(
        "--compile",
        action="store_true",
    )

    parser.add_argument(
        "--check",
        action="store_true",
    )

    args = parser.parse_args()

    if args.init:
        for lang in args.init:
            init_language(lang)

    if args.update:
        update_languages()

    if args.compile:
        compile_mo()

    if args.check:
        check()