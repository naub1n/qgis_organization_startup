from qgis.core import Qgis, QgsSettings

from qgis_organization_startup.common.base import BaseStartup


class CheckArcgisConnections(BaseStartup):

    @BaseStartup.template_function(
        "arcgis_connections",
        "Vérification des connexions ArcGIS Server"
    )
    def check(self) -> None:
        cnx_name = self._cfg.get("name", "")
        cnx_headers = self._cfg.get("headers", [])
        cnx_url = self._cfg.get("url", "")
        cnx_community_endpoint = self._cfg.get("community_endpoint", "")
        cnx_content_endpoint = self._cfg.get("content_endpoint", "")
        cnx_authcfg = self._cfg.get("authcfg", "")
        cnx_username = self._cfg.get("username", "")
        cnx_password = self._cfg.get("password", "")
        cnx_remove = self._cfg.get("remove", False)

        s = QgsSettings()
        s.beginGroup('connections/arcgisfeatureserver/items')

        s.setValue(f"{cnx_name}/url", cnx_url)
        s.setValue(f"{cnx_name}/community-endpoint", cnx_community_endpoint)
        s.setValue(f"{cnx_name}/content-endpoint", cnx_content_endpoint)
        s.setValue(f"{cnx_name}/authcfg", cnx_authcfg)
        s.setValue(f"{cnx_name}/username", cnx_username)
        s.setValue(f"{cnx_name}/password", cnx_password)

        for header in cnx_headers:
            s.setValue(f"{cnx_name}/http-header/{header.get("key")}", header.get("value"))

        if cnx_remove:
            s.remove(cnx_name)
            self._log(self._tr("Connexion ArcGIS '{}' supprimée").format(cnx_name), Qgis.Info)

        else:
            self._log(self._tr("Connexion ArcGIS '{}' ajoutée/modifiée").format(cnx_name), Qgis.Info)
