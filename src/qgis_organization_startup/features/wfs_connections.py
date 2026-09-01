from qgis.core import Qgis, QgsSettings

from qgis_organization_startup.common.base import BaseStartup


class CheckWFSConnections(BaseStartup):
    @BaseStartup.template_function(
        "wfs_connections",
        "Vérification des connexions WFS"
    )
    def check(self) -> None:
        cnx_name = self._cfg.get("name", "")
        cnx_ignoreaxisorientation = self._cfg.get("ignoreAxisOrientation", False)
        cnx_invertaxisorientation = self._cfg.get("invertAxisOrientation", False)
        cnx_maxnumfeatures = self._cfg.get("maxnumfeatures", "")
        cnx_pagesize = self._cfg.get("pagesize", 1000)
        cnx_pagingenabled = self._cfg.get("pagingenabled", True)
        cnx_prefercoordinatesforwfst11 = self._cfg.get("preferCoordinatesForWfsT11", False)
        cnx_url = self._cfg.get("url", "")
        cnx_version = self._cfg.get("version", "auto")
        cnx_authcfg = self._cfg.get("authcfg", "")
        cnx_username = self._cfg.get("username", "")
        cnx_password = self._cfg.get("password", "")
        cnx_remove = self._cfg.get("remove", False)

        s = QgsSettings()

        s.beginGroup('connections/ows/items/wfs/connections/items')

        s.setValue(f"{cnx_name}/ignore-axis-orientation", cnx_ignoreaxisorientation)
        s.setValue(f"{cnx_name}/invert-axis-orientation", cnx_invertaxisorientation)
        s.setValue(f"{cnx_name}/max-num-features", cnx_maxnumfeatures)
        s.setValue(f"{cnx_name}/page-size", cnx_pagesize)
        s.setValue(f"{cnx_name}/paging-enabled", cnx_pagingenabled)
        s.setValue(f"{cnx_name}/prefer-coordinates-for-wfs-T11", cnx_prefercoordinatesforwfst11)
        s.setValue(f"{cnx_name}/url", cnx_url)
        s.setValue(f"{cnx_name}/version", cnx_version)
        s.setValue(f"{cnx_name}/authcfg", cnx_authcfg)
        s.setValue(f"{cnx_name}/username", cnx_username)
        s.setValue(f"{cnx_name}/password", cnx_password)

        if cnx_remove:
            s.remove(cnx_name)
            self._log(self._tr("Connexion WFS '{}' supprimée").format(cnx_name), Qgis.Info)

        else:
            self._log(self._tr("Connexion WFS '{}' ajoutée/modifiée").format(cnx_name), Qgis.Info)


            # # Pour QGIS < 3.34
            # s.beginGroup('qgis')
            # s.beginGroup('connections-wfs')
            #
            # s.setValue("%s/ignoreAxisOrientation" % cnx_name, cnx_ignoreaxisorientation)
            # s.setValue("%s/invertAxisOrientation" % cnx_name, cnx_invertaxisorientation)
            # s.setValue("%s/maxnumfeatures" % cnx_name, cnx_maxnumfeatures)
            # s.setValue("%s/pagesize" % cnx_name, cnx_pagesize)
            # s.setValue("%s/pagingenabled" % cnx_name, cnx_pagingenabled)
            # s.setValue("%s/preferCoordinatesForWfsT11" % cnx_name, cnx_prefercoordinatesforwfst11)
            # s.setValue("%s/url" % cnx_name, cnx_url)
            # s.setValue("%s/version" % cnx_name, cnx_version)
            #
            # if cnx_remove:
            #     s.remove(cnx_name)
            #
            # s = QgsSettings()
            # s.beginGroup('qgis')
            # s.beginGroup('WFS')
            # s.setValue("%s/authcfg" % cnx_name, cnx_authcfg)
            # s.setValue("%s/username" % cnx_name, cnx_username)
            # s.setValue("%s/password" % cnx_name, cnx_password)
            #
            # if cnx_remove:
            #     s.remove(cnx_name)