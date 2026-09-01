from qgis.core import Qgis, QgsSettings

from qgis_organization_startup.common.base import BasePluginSetup


class SetupQWCTools(BasePluginSetup):

    @BasePluginSetup.template_setup("qwc2_tools")
    def setup(self, plugin_config: dict) -> None:

        default_authent_id = plugin_config.get("default_authent_id", "")
        default_token_validity = plugin_config.get("default_token_validity", 60)
        default_type_authent = plugin_config.get("default_type_authent", 0)
        default_url_authent = plugin_config.get("default_url_authent", "")
        tenant_list = plugin_config.get("tenant_list", {})
        replace_tenant_config = plugin_config.get("replace_tenant_config", {})

        tenant_config_keys = list(tenant_list)

        s = QgsSettings()
        current_tenant_list = s.value("QWC Tools/tenant_list", {})

        for tc in tenant_config_keys:

            if tenant_list[tc].get("delete", False):

                del tenant_list[tc]

                if tc in list(current_tenant_list):
                    self._log(self._tr("Suppression de la configuration '{}'.").format(tc), Qgis.Info)
                    del current_tenant_list[tc]

                continue

            if not replace_tenant_config:
                if tc in list(current_tenant_list):
                    self._log(self._tr("La configuration '{}' existe déjà.").format(tc), Qgis.Warning)
                    del tenant_list[tc]
                    continue

            if "url_base" not in tenant_list[tc]:
                self._log(self._tr("Pas d'URL de base configurée dans la configuration '%s'. Elle sera ignorée.").format(tc),
                         Qgis.Warning)
                del tenant_list[tc]
                continue

            if "authent_id" not in tenant_list[tc]:
                tenant_list[tc]["authent_id"] = default_authent_id

            if "token_validity" not in tenant_list[tc]:
                tenant_list[tc]["token_validity"] = default_token_validity

            if "type_authent" not in tenant_list[tc]:
                tenant_list[tc]["type_authent"] = default_type_authent

            if "url_authent" not in tenant_list[tc]:
                if default_url_authent:
                    tenant_list[tc]["url_authent"] = default_url_authent
                else:
                    tenant_list[tc]["url_authent"] = tenant_list[tc]["url_base"].rstrip('/') + '/auth/login'

            if "url_publish" not in tenant_list[tc]:
                tenant_list[tc]["url_publish"] = tenant_list[tc]["url_base"].rstrip('/') + '/publish'

        full_tenant_list = {**current_tenant_list, **tenant_list}

        s.setValue("QWC Tools/tenant_list", full_tenant_list)