import os
import re
import configparser

from qgis.core import Qgis, QgsSettings

from qgis_organization_startup.common.base import BaseStartup


class CheckPGServices(BaseStartup):

    @BaseStartup.template_function(
        "pg_services_configs",
        "Paramétrage du fichier pg_service.conf"
    )
    def check(self) -> None:
        pgsc_services = self._cfg.get("pg_services", [])

        sys_pgservice_path = os.environ.get("PGSERVICEFILE", "")

        s = QgsSettings()
        s.beginGroup('qgis')
        current_custom_vars = s.value("customEnvVars", [])

        qgis_pgservice_path = ""

        for var in current_custom_vars:
            var_infos = re.split('\||=', var)
            if var_infos[1].lower() == "pgservicefile":
                qgis_pgservice_path = var_infos[2]

        if not sys_pgservice_path and not qgis_pgservice_path:
            self._log(self._tr("Le chemin vers le fichier pg_service.conf n'est pas défini"), Qgis.Warning)
            return

        pgservice_path = qgis_pgservice_path or sys_pgservice_path

        config = configparser.ConfigParser()
        config.read(pgservice_path)

        for service in pgsc_services:
            name = service.get("name", "")
            host = service.get("host", "")
            port = service.get("port", "")
            user = service.get("user", "")

            if not name:
                self._log(self._tr("Un service n'a pas de nom de défini"), Qgis.Warning)
                continue

            if not name in config.sections():
                config[name] = {}

            config[name]["host"] = host
            config[name]["port"] = port

            if user == '$email$':
                user = self._user.user_email

            config[name]["user"] = user

        with open(pgservice_path, 'w') as configfile:
            config.write(configfile)