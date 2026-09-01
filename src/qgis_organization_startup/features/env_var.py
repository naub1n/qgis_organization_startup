from qgis.core import Qgis, QgsSettings

from qgis_organization_startup.common.base import BaseStartup


class CheckEnvVar(BaseStartup):

    @BaseStartup.template_function(
        f_key="customEnvVars",
        title="Définition des variables d'environnement personnalisées"
    )
    def check(self) -> None:
        """
        Lance le test sur le lecteur réseau (Windows uniquement)

        :return:
        """
        var_name = self._cfg.get("name", "")
        var_value = self._cfg.get("value", "")

        if var_name:
            s = QgsSettings()
            s.beginGroup('qgis')
            s.setValue("customEnvVarsUse", True)

            current_custom_vars = s.value("customEnvVars", [])

            if isinstance(current_custom_vars, str):
                current_custom_vars = [current_custom_vars]

            new_custom_vars = []

            # Ajout des autres variables d'environnement sans faire de doublon
            for current_var in current_custom_vars:
                if "|" + var_name + "=" not in current_var:
                    new_custom_vars.append(current_var)

            self._log(self._tr("Déclaration de la variable d'environnement {}").format(var_name), Qgis.Info)
            new_custom_vars.append("overwrite|%s=%s" % (var_name, var_value))

            s.setValue("customEnvVars", new_custom_vars)