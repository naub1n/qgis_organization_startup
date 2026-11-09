import json

from qgis.core import Qgis
from qgis.PyQt.QtCore import QUrl, QFileInfo
from urllib.parse import urlparse
from importlib.resources import files

from qgis_organization_startup.common.logger import StartupLogger
from qgis_organization_startup.common.profiler import StartupProfiler
from qgis_organization_startup.common.request import StartupRequest
from qgis_organization_startup.common.translation import gettext_tr

class StartupConfig:
    def __init__(self, uri: str, logger: StartupLogger, profiler: StartupProfiler) -> None:
        """
        Lecture de la configuration globale

        :param uri: URI vers le fichier json contenant les paramétrages
        """

        self.uri = uri

        self._sp = profiler
        self._request = StartupRequest(logger)
        self._log = logger.log
        self._error = logger.error
        self._tr = gettext_tr()

        self.config = self._read_conf()

    def _read_conf(self):

        p_name = self._tr("Lecture de la configuration globale")
        self._log(p_name, Qgis.Info)
        self._sp.start(p_name)

        config = {}

        try:
            scheme = urlparse(self.uri).scheme

            if scheme in ["http", "https"]:
                url = QUrl(self.uri)
                config = self._request.get_json(url)

            elif scheme == "file":
                url = QUrl(self.uri)
                file_info = QFileInfo(url.toLocalFile())
                path = file_info.absoluteFilePath()

                with open(path, encoding="utf-8") as f:
                    config = json.load(f)

            else:
                self._log(self._tr("L'URI du fichier de configuration n'est pas valide"), Qgis.Critical)

        except Exception as e:
            self._error(self._tr("Erreur lors de la lecture de la configuration globale: {}").format(str(e)))

        # Validation du fichier de config
        try:
            from jsonschema import validate

            schema_path = files("qgis_organization_startup").joinpath("schema/organization_startup_config_schema.json")
            schema = json.loads(schema_path.read_text(encoding="utf-8"))

            validate(instance=config, schema=schema)

        except Exception as e:
            self._error(self._tr("Erreur dans la vérification de la configuration globale: {}").format(str(e)))
            # Configuration invalide : on arrête le paramétrage
            config = {}

        self._sp.end()

        return config