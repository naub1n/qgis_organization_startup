from fnmatch import fnmatch
from qgis.core import Qgis, QgsProject, QgsDataSourceUri

from qgis_organization_startup.common.base import BaseStartup


class CheckListenerSessionRole(BaseStartup):

    @BaseStartup.template_function(
        "disable_session_role",
        "Vérification du role de session à l'ajout de couches"
    )
    def check(self) -> None:
        self.host_patterns = self._cfg.get("host_patterns", [])

        if isinstance(self.host_patterns, str):
            self.host_patterns = [self.host_patterns]

        if self.host_patterns:
            self._log(self._tr("Désactivation du rôle de session lors de l'ajout d'une couche à partir des hosts {}").format(", ".join(self.host_patterns)), Qgis.Info)

            try:
                QgsProject.instance().layerWasAdded.disconnect(self.on_layer_added)
            except TypeError:
                pass

            QgsProject.instance().layerWasAdded.connect(self.on_layer_added)

    def remove_session_role_param(self, layer):
        new_uri = QgsDataSourceUri(layer.dataProvider().dataSourceUri(False))
        if ({'session_role', 'host'}).issubset(new_uri.parameterKeys()):
            if any(fnmatch(new_uri.host(), pattern) for pattern in self.host_patterns):
                new_uri.removeParam("session_role")
                layer.setDataSource(new_uri.uri(False), layer.name(), layer.providerType())

    def on_layer_added(self, layer):
        self.remove_session_role_param(layer)