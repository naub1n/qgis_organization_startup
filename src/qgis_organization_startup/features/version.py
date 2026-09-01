from qgis.core import Qgis
from qgis.utils import iface

from qgis_organization_startup.common.base import BaseStartup

class CheckVersion(BaseStartup):
    @BaseStartup.template_function(
        "managed_qgis_versions",
        "Vérification de la version de QGIS"
    )
    def check(self) -> None:
        e_versions = self._cfg.get("versions", [])

        c_version = Qgis.QGIS_VERSION_INT

        if not c_version in e_versions:
            warn_msg = self._tr("Vous utilisez une version ({}) non gérée par votre administrateur ({}). Le paramétrage ne sera pas appliqué.").format(c_version, e_versions)
            iface.messageBar().pushMessage(warn_msg, level=Qgis.Warning, duration=10)
            self._error(warn_msg)


