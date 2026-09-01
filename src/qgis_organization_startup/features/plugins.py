import pyplugin_installer

from qgis.core import Qgis, QgsSettings
from qgis.utils import unloadPlugin

from qgis_organization_startup.common.base import BaseStartup
from qgis_organization_startup.features.plugins_conf import (
    SetupMenuFromProject,
    SetupCustomNewsFeed,
    SetupQWCTools,
    SetupCreerMenu
)


class CheckPlugins(BaseStartup):

    @BaseStartup.template_function(
        "plugins",
        "Vérification des plugins requis"
    )
    def check(self) -> None:

        plugins_list = self._cfg.get("names", [])
        plugins_delete_mode = self._cfg.get("delete_mode", None)

        pi_inst = pyplugin_installer.instance()

        plugins_data = pyplugin_installer.installer_data.plugins

        available_plugins_keys = plugins_data.all().keys()
        upgradable_plugins_keys = plugins_data.allUpgradeable().keys()
        
        s = QgsSettings()

        if plugins_delete_mode in ["disable", "uninstall"]:
            for plugin in plugins_list:
                self._log(self._tr("Désactivation du plugin {}").format(str(plugin)), Qgis.Info)
                unloadPlugin(plugin)
                s.setValue("PythonPlugins/" + plugin, False)

                if plugins_delete_mode == "uninstall":
                    self._log(self._tr("Désinstallation du plugin {}").format(str(plugin)), Qgis.Info)
                    pi_inst.uninstallPlugin(plugin)
                    s.remove("PythonPlugins/" + plugin)

        else:
            for plugin in plugins_list:
                if plugin in available_plugins_keys:

                    is_installed = plugins_data.all()[plugin]['installed']
                    is_upgradable = plugin in upgradable_plugins_keys

                    if not is_installed or is_upgradable:
                        self._log(self._tr("Installation/Mise à jour du paquet {}").format(str(plugin)), Qgis.Info)
                        pi_inst.installPlugin(plugin)

                    else:
                        plugin_is_active = s.value("/PythonPlugins/" + plugin, False, type=bool)

                        if not plugin_is_active:
                            self._log(self._tr("Activation du plugin {}").format(str(plugin)), Qgis.Info)
                            s.setValue("PythonPlugins/" + plugin, True)

                        self._log(self._tr("Le paquet {} est installé et à jour").format(str(plugin)), Qgis.Info)
                else:
                    self._log(self._tr("Le paquet {} est indisponible").format(str(plugin)), Qgis.Warning)

class CheckPluginsConfigs(BaseStartup):
    @BaseStartup.template_function(
        "plugins_configs",
        "Configuration des plugins"
    )
    def check(self) -> None:
        plugin_name = self._cfg.get("plugin_name", "")
        plugin_config = self._cfg.get("config", {})

        setup = None
        if plugin_name == "menu_from_project":
            setup = SetupMenuFromProject

        if plugin_name == "creer_menus":
            setup = SetupCreerMenu

        if plugin_name == "custom_news_feed":
            setup = SetupCustomNewsFeed

        if plugin_name == "qwc2_tools":
            setup = SetupQWCTools

        if setup:
            setup(self._cfg, self._user, self.logger, self._sp).setup(plugin_config)



