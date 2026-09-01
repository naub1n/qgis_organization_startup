from qgis_organization_startup.common.config import StartupConfig
from qgis_organization_startup.common.logger import StartupLogger
from qgis_organization_startup.common.translation import gettext_tr
from qgis_organization_startup.common.profiler import StartupProfiler
from qgis_organization_startup.common.user import UserInfo

from qgis_organization_startup.features import ALL_FEATURES

_ = gettext_tr()

class QgisOrganizationStartup:
    def __init__(self, conf_url: str, profiler_group_name: str, logger_tag: str, raise_on_error: bool = False):
        """

        :param conf_url: URL du fichier de configuration JSON (supporte https:// ou file:// )
        :param profiler_group_name: Nom du groupe qui sera créé dans le profiler QGIS
        :param logger_tag: Nom de l'onglet dans le journal des messages de QGIS
        :param raise_on_error: Léve une erreur python lorsque qu'une configuration échoue
        """
        self.conf_url = conf_url
        self.raise_on_error = raise_on_error
        self.logger_tag = logger_tag

        self._sp = StartupProfiler(profiler_group_name)

        self._features = []

    def start(self):
        """
        Lance le processus de paramétrage de QGIS

        :return:
        """

        logger = StartupLogger(self.logger_tag, self.raise_on_error)

        config = StartupConfig(self.conf_url, logger, self._sp).config

        if not config:
            return

        user_info = UserInfo(config, logger)

        for f in ALL_FEATURES:
            # Permet de concerver les classe dans la durée de vie de la session QGIS (surtout pour les signaux)
            feature = f(
                config,
                user_info,
                logger,
                self._sp
            )

            self._features.append(feature)

            if not feature.check():
                break

