import uuid

from qgis.core import Qgis, QgsSettings

from qgis_organization_startup.common.base import BasePluginSetup


class SetupMenuFromProject(BasePluginSetup):

    @BasePluginSetup.template_setup("menu_from_project")
    def setup(self, plugin_config: dict) -> None:

        options = plugin_config.get("options", {})

        s = QgsSettings()
        s.beginGroup('menu_from_project')

        is_setup_visible = options.get("is_setup_visible", None)
        option_toolip = options.get("optionTooltip", None)
        option_create_group = options.get("optionCreateGroup", None)
        option_load_all = options.get("optionLoadAll", None)
        option_source_md = options.get("optionSourceMD", None)
        browser_name = options.get("browser_name", None)

        if is_setup_visible is not None:
            s.setValue("is_setup_visible", is_setup_visible)

        if option_toolip is not None:
            s.setValue("optionTooltip", option_toolip)

        if option_create_group is not None:
            s.setValue("optionCreateGroup", option_create_group)

        if option_load_all is not None:
            s.setValue("optionLoadAll", option_load_all)

        if option_source_md is not None:
            s.setValue("optionSourceMD", option_source_md)

        if browser_name is not None:
            s.setValue("browser_name", browser_name)

        projects = plugin_config.get("projects", [])

        # Liste des noms de projets à ajouter (ils seront placés au début)
        project_names = []
        for project in projects:
            project_names.append(project.get("name", ""))

        # Lecture des projets existants
        current_projects = []
        cs = QgsSettings()
        cs.beginGroup('menu_from_project')
        size = cs.beginReadArray("projects")

        for current_project_id in cs.childGroups():
            if int(current_project_id) <= size:
                cs.beginGroup(current_project_id)
                # Si le nom du projet ne fait pas partie de ceux à ajouter alors il est conservé
                cpn = cs.value("name")
                if not cpn in project_names:
                    project = {
                        "id": cs.value("id"),
                        "file": cs.value("file"),
                        "location": cs.value("location"),
                        "name": cpn,
                        "type_storage": cs.value("type_storage"),
                        "cache_config": {
                            "refresh_days_period": cs.value("cache_config/refresh_days_period", type=int),
                            "enable": cs.value("cache_config/enable", type=bool),
                            "cache_validation_uri": cs.value("cache_config/cache_validation_uri")
                        }
                    }
                    current_projects.append(project)
                    self._log(self._tr("Le projet '{}' est conservé").format(cpn), Qgis.Info)

                cs.endGroup()

        s.remove("projects")

        if not plugin_config.get("replace_projects", False):
            projects.extend(current_projects)

        s.beginWriteArray("projects")
        try:
            for i, project in enumerate(projects):

                project_name = project.get("name", "")

                s.setArrayIndex(i)
                s.setValue("file", self._format(project.get("file", "")))
                s.setValue("name", project_name)
                s.setValue("location", project.get("location", ""))
                s.setValue("type_storage", project.get("type_storage", ""))
                s.setValue("id", project.get("id", str(uuid.uuid4())))

                cache_period = project.get("cache_config", {}).get("refresh_days_period", 0)
                cache_enable = project.get("cache_config", {}).get("enable", False)
                cache_uri = self._format(project.get("cache_config", {}).get("cache_validation_uri", ""))

                if cache_period == 0 and cache_enable == True and not cache_uri:
                    self._log(self._tr("Le projet '{}' n'a pas de cache de configuré, le cache est désactivé.").format(project_name),
                             Qgis.Warning)
                    cache_enable = False

                s.setValue("cache_config/refresh_days_period", cache_period)
                s.setValue("cache_config/enable", cache_enable)
                s.setValue("cache_config/cache_validation_uri", cache_uri)
        finally:
            s.endArray()