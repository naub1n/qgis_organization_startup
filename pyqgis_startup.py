# Script qui sera lancé au démarrage de QGIS
# Son chemin d'accès est à déclarer dans la variable d'environnement PYQGIS_STARTUP

import os
import platform
import urllib.request
import ssl
import subprocess
import tempfile
import re
import logging
import sys

from pathlib import Path

STARTUP_URI = os.getenv("PYQGIS_STARTUP_QOS_STARTUP_URI")
QGIS_ORGANIZATION_STARTUP_PKG_URI = os.getenv("PYQGIS_STARTUP_QOS_PKG_URI")
LOG_FILENAME = 'pyqgis_startup.log'

log_path = Path(os.getenv("PYQGIS_STARTUP")).resolve().parent / LOG_FILENAME

# vide le fichier de log au démarrage
log_path.write_text("", encoding="utf-8")

logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

startup_code = """
import os

from importlib.util import find_spec
from qgis.core import QgsMessageLog, Qgis

check_qos_pkg = find_spec("qgis_organization_startup")

logger_tag = "Qgis Organization Startup"

if not check_qos_pkg:
    QgsMessageLog.logMessage("Le paquet qgis_organization_startup ne semble pas installé", logger_tag, level=Qgis.Critical, notifyUser=False)
else:

    from qgis_organization_startup import QgisOrganizationStartup
    
    config_url = os.getenv("PYQGIS_STARTUP_QOS_CONFIG_URI")
    
    QOS = QgisOrganizationStartup(
        config_url,
        "QgisOrganisationStartup",
        logger_tag,
        False)
    
    QOS.start()
"""

def qgis_major_version():
    result = subprocess.run(
        [sys.executable, "--version"],
        capture_output=True,
        text=True,
        check=True,
    )

    output = result.stdout + result.stderr

    match = re.search(r"QGIS\s+(\d+)", output)

    if not match:
        raise RuntimeError(
            f"Impossible de déterminer la version QGIS : {output!r}"
        )

    return int(match.group(1))

    #TODO: Rendre compatible avec Linux/Ubuntu


class SetupQgisOrganisationStartup:
    def __init__(self, startup_uri: str | None, qgis_org_startup_uri: str, qgis_major_version: int = 3):
        self.startup_uri = startup_uri
        self.qgis_org_startup_uri = qgis_org_startup_uri
        self.qgis_major_version = qgis_major_version

    def setup(self) -> None:

        try:
            if self.startup_uri:
                logging.info(f"## Récupération du fichier startup.py via {self.startup_uri}")
                # Téléchargement du fichier startup.py pour QGIS
                self._download(self.startup_uri, self._get_qgis_config_path(), "startup.py")
            else:
                logging.info(f"## Création du fichier startup.py par défaut")
                # Ecriture du fichier startup.py par défaut
                with open(self._get_qgis_config_path() / "startup.py", "w", encoding="utf-8") as f:
                    f.write(startup_code)

            logging.info(f"## Installation du paquet Qgis Organization Startup")

            if not self.qgis_org_startup_uri:
                logging.error(f"Aucune URI d'indiquée pour le parquet Qgis Organization Startup. Installation annulée.")
                return

            # Installation du paquet Qgis Organization Startup
            qos_whl_path = self._download(self.qgis_org_startup_uri, Path(tempfile.gettempdir()))
            self._install_wheel(qos_whl_path)

        except Exception as e:
            logging.exception(str(e))

    def _download(self, uri: str, output_dir_path: Path, output_filename: str = None) -> Path:
        """
        Télécharge un fichier à partir de son URI

        :param uri: URI du fichier. Supporte https://, http:// et file://
        :param output_dir_path: Chemin du dossier de destination

        :return: Chemin du fichier téléchargé
        """

        output_dir_path.mkdir(parents=True, exist_ok=True)

        if uri.startswith("https://") or uri.startswith("http://") or uri.startswith("file://"):
            try:
                ctx = ssl.create_default_context() if uri.startswith("https://") else None

                with urllib.request.urlopen(uri, timeout=10, context=ctx) as response:

                    if output_filename:
                        filename = output_filename

                    else:
                        filename = self._get_filename(uri, response.headers)

                    output_file_path = output_dir_path / filename

                    logging.info(f"Récupération de la source du fichier {filename}")

                    with open(output_file_path, "wb") as f:
                        f.write(response.read())

                logging.info("Récupération du fichier terminée avec succès")

                return output_file_path

            except Exception as e:
                raise RuntimeError(f"Erreur lors de la récupération de {uri} : {e}")

        else:
            raise RuntimeError("URI non supportée")

    def _get_filename(self, uri: str, headers) -> str:
        cd = headers.get("Content-Disposition")

        if cd:
            match = re.search(r'filename="?([^"]+)"?', cd)
            if match:
                return match.group(1)

        return Path(uri).name

    def _get_qgis_config_path(self) -> Path:
        """
        Récupére le chemin vers le dossier de configration de QGIS

        :return:
        """

        custom_path = os.environ.get("QGIS_CUSTOM_CONFIG_PATH")
        if custom_path:
            return Path(custom_path)

        if platform.system() == "Windows":
            base = Path(os.environ.get("APPDATA", Path.home()))

        elif platform.system() == "darwin":
            base = Path.home() / "Library" / "Application Support"

        elif platform.system() == "Linux":
            base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".local" / "share"))

        else:
            raise RuntimeError("OS non supporté")

        return base / "QGIS" / f"QGIS{self.qgis_major_version}"

    def _install_wheel(self, wheel_path: Path) -> None:
        cmd = [
            "pip",
            "install",
            str(wheel_path)
        ]

        logging.info(f"Installation de {wheel_path.name}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )

        logging.info(result.stdout)

        if result.returncode != 0:
            logging.error(result.stderr)

        else:
            logging.info("Installation réalisée avec succès")

logging.info("Identification de la version majeur de QGIS")

QGIS_MAJOR_VERSION = qgis_major_version()

logging.info(f"QGIS major = {QGIS_MAJOR_VERSION}")

logging.info("Démarrage pyqgis_startup")

SetupQgisOrganisationStartup(STARTUP_URI, QGIS_ORGANIZATION_STARTUP_PKG_URI, QGIS_MAJOR_VERSION).setup()
