from qgis.core import QgsSettings

from qgis_organization_startup.common.base import BaseStartup


class CheckQGISSettings(BaseStartup):

    @BaseStartup.template_function(
        "qgis_settings",
        "Vérification des paramètres globaux de QGIS"
    )
    def check(self) -> None:
        settings = self._cfg.get("settings", [])

        s = QgsSettings()

        for setting in settings:
            setting_path = setting.get("path", "")
            setting_value = setting.get("value", "")
            if setting_path:
                s.setValue(setting_path, setting_value)