from qgis.core import QgsSettings

from qgis_organization_startup.common.base import BasePluginSetup


class SetupCustomNewsFeed(BasePluginSetup):

    @BasePluginSetup.template_setup("custom_news_feed")
    def setup(self, plugin_config: dict):
        config_path = plugin_config.get("config_path", "")

        if config_path:
            QgsSettings().setValue("CustomNewsFeed/json_file_path", config_path)
