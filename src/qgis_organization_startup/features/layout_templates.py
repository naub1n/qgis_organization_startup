from qgis.core import QgsApplication, QgsSettings

from qgis_organization_startup.common.base import BaseStartup


class CheckLayoutTemplates(BaseStartup):
    @BaseStartup.template_function(
        "composer_templates",
        "Vérification des modèles"
    )
    def check(self) -> None:
        t_path = self._cfg.get("path", "")

        layouts = QgsApplication.layoutTemplatePaths()

        if t_path not in layouts:
            layouts.append(t_path)

            s = QgsSettings()
            s.beginGroup('layout')

            s.setValue("search-paths-for-templates", layouts)