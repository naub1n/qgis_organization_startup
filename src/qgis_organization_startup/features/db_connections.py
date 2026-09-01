from qgis.core import Qgis, QgsProviderRegistry, QgsDataSourceUri

from qgis_organization_startup.common.base import BaseStartup


class CheckDbConnections(BaseStartup):

    @BaseStartup.template_function(
        "db_connections",
        "Vérification des connexions aux bdd"
    )
    def check(self) -> None:

        cnx_provider = self._cfg.get("qgis_provider", "")
        cnx_name = self._format(self._cfg.get("name", ""))
        cnx_service = self._cfg.get("service", "")
        cnx_host = self._format(self._cfg.get("host", ""))
        cnx_port = self._cfg.get("port", "")
        cnx_dbname = self._format(self._cfg.get("dbname", ""))
        cnx_auth_id = self._cfg.get("auth_id", "")
        cnx_get_role = self._cfg.get("get_role", False)
        cnx_configs = self._cfg.get("configs", {})

        provider = QgsProviderRegistry.instance().providerMetadata(cnx_provider)
        uri = QgsDataSourceUri()
        if cnx_service:
            uri.setConnection(aService=cnx_service,
                              aDatabase=cnx_dbname,
                              aUsername=None,
                              aPassword=None,
                              authConfigId=cnx_auth_id)
        else:
            uri.setConnection(aHost=cnx_host,
                              aPort=cnx_port,
                              aDatabase=cnx_dbname,
                              aUsername=None,
                              aPassword=None,
                              authConfigId=cnx_auth_id)

        config = {
            "allowGeometrylessTables": cnx_configs.get("allowGeometrylessTables", False),
            "dontResolveType": cnx_configs.get("dontResolveType", False),
            "estimatedMetadata": cnx_configs.get("estimatedMetadata", False),
            "geometryColumnsOnly": cnx_configs.get("geometryColumnsOnly", True),
            "metadataInDatabase": cnx_configs.get("metadataInDatabase", False),
            "projectsInDatabase": cnx_configs.get("projectsInDatabase", False),
            "publicOnly": cnx_configs.get("publicOnly", False),
            "savePassword": cnx_configs.get("savePassword", False),
            "saveUsername": cnx_configs.get("saveUsername", False),
            "session_role": self._user.user_role if cnx_get_role else ''
        }
        self._log(self._tr("Ajout/Restauration de la connection '{}'.").format(cnx_name), Qgis.Info)
        new_conn = provider.createConnection(None, config)
        new_conn.setUri(uri.uri(expandAuthConfig=False))
        # La connexion est ajoutée si inexistante ou remplacée si elle existe déjà
        new_conn.store(cnx_name)
