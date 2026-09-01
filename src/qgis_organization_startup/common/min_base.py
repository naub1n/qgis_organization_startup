from abc import ABC

from qgis_organization_startup.common.translation import gettext_tr
from qgis_organization_startup.common.logger import StartupLogger
from qgis_organization_startup.common.request import StartupRequest


class MinBaseStartup(ABC):
    def __init__(self, config: dict, logger: StartupLogger):
        self._config = config
        self.logger = logger

        self._log = logger.log
        self._error = logger.error
        self._tr = gettext_tr()
        self._request = StartupRequest(logger)
