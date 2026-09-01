from qgis.core import QgsSettings

from qgis_organization_startup.common.base import BasePluginSetup


class SetupCreerMenu(BasePluginSetup):

    @BasePluginSetup.template_setup("creer_menus")
    def setup(self, plugin_config: dict):
        file_menus = plugin_config.get("fileMenus", "")

        if file_menus:
            QgsSettings().setValue("PluginCreerMenus/fileMenus", file_menus)