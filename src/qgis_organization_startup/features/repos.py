import pyplugin_installer

from qgis.core import QgsSettings
from pyplugin_installer.installer_data import repositories, plugins, reposGroup

from qgis_organization_startup.common.base import BaseStartup


class CheckRepositories(BaseStartup):
    @BaseStartup.template_function(
        "plugins_repositories",
        "Vérification des dépôts de plugins"
    )
    def check(self) -> None:
        """
        Permet d'ajouter ou remplacer la déclaration d'un dépôt de plugins QGIS

        :return:
        """
        repo_name = self._cfg.get("name", "")
        repo_url = self._format(self._cfg.get("url", ""))
        repo_authcfg = self._cfg.get("authcfg", "")

        pyplugin_inst = pyplugin_installer.instance()
        pyplugin_installer.instance().fetchAvailablePlugins(True)

        s = QgsSettings()

        s.beginGroup(reposGroup)
        if repo_name in repositories.all():
            s.remove(repo_name)

        s.setValue(repo_name + "/url", repo_url)
        s.setValue(repo_name + "/authcfg", repo_authcfg)
        s.setValue(repo_name + "/enabled", True)

        plugins.removeRepository(repo_name)
        pyplugin_inst.reloadAndExportData()