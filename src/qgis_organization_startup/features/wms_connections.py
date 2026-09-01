from qgis.core import Qgis, QgsSettings

from qgis_organization_startup.common.base import BaseStartup


class CheckWMSConnections(BaseStartup):

    @BaseStartup.template_function(
        "wms_connections",
        "Vérification des connexions WMS/WMTS"
    )
    def check(self) -> None:
        cnx_name = self._cfg.get("name", "")
        cnx_dpimode = self._cfg.get("dpiMode", 7)
        cnx_ignoreaxisorientation = self._cfg.get("ignoreAxisOrientation", False)
        cnx_ignoregetfeatureinfouri = self._cfg.get("ignoreGetFeatureInfoURI", False)
        cnx_ignoregetmapuri = self._cfg.get("ignoreGetMapURI", False)
        cnx_invertaxisorientation = self._cfg.get("invertAxisOrientation", False)
        cnx_reportedlayerextents = self._cfg.get("reportedLayerExtents", False)
        cnx_smoothpixmaptransform = self._cfg.get("smoothPixmapTransform", False)
        cnx_url = self._cfg.get("url", "")
        cnx_authcfg = self._cfg.get("authcfg", "")
        cnx_username = self._cfg.get("username", "")
        cnx_password = self._cfg.get("password", "")
        cnx_remove = self._cfg.get("remove", False)

        s = QgsSettings()

        s.beginGroup('connections/ows/items/wms/connections/items')

        s.setValue(f"{cnx_name}/dpi-mode", cnx_dpimode)
        s.setValue(f"{cnx_name}/ignore-axis-orientation", cnx_ignoreaxisorientation)
        s.setValue(f"{cnx_name}/invert-axis-orientation", cnx_invertaxisorientation)
        s.setValue(f"{cnx_name}/ignore-get-feature-info-uri", cnx_ignoregetfeatureinfouri)
        s.setValue(f"{cnx_name}/ignore-get-map-uri", cnx_ignoregetmapuri)
        s.setValue(f"{cnx_name}/reported-layer-extents", cnx_reportedlayerextents)
        s.setValue(f"{cnx_name}/smooth-pixmap-transform", cnx_smoothpixmaptransform)
        s.setValue(f"{cnx_name}/url", cnx_url)
        s.setValue(f"{cnx_name}/authcfg", cnx_authcfg)
        s.setValue(f"{cnx_name}/username", cnx_username)
        s.setValue(f"{cnx_name}/password", cnx_password)

        if cnx_remove:
            s.remove(cnx_name)
            self._log(self._tr("Connexion WMS/WMTS '{}' supprimée").format(cnx_name), Qgis.Info)

        else:
            self._log(self._tr("Connexion WMS/WMTS '{}' ajoutée/modifiée").format(cnx_name), Qgis.Info)
