import os
import subprocess
import re

from qgis.core import Qgis
from qgis.PyQt.QtCore import QUrl, QUrlQuery

from qgis_organization_startup.common.logger import StartupLogger
from qgis_organization_startup.common.format_str import format_str
from qgis_organization_startup.common.min_base import MinBaseStartup
from qgis_organization_startup.common.deploy_env import StartupDeployEnv


class UserInfo(MinBaseStartup):
    def __init__(self, config: dict, logger: StartupLogger):
        super().__init__(config, logger)

        self.user_d_env, self.user_d_env_suffix = StartupDeployEnv(config, logger).get_env()

        self.user_name = os.environ.get("username", "").lower()
        self.user_os = os.name
        self.user_domain = os.environ.get("userdomain", "").lower()
        self.user_email = self._get_user_email()
        self.user_fqdn = self._get_user_fqdn()
        self.user_zone = self._get_user_zone()

        self.user_role = self._get_user_role()


    def _get_user_email(self) -> str | None:
        """
        Permet de récupérer l'adresse email de l'utilisateur, ou du moins, l'identifiant de son compte d'entreprise

        :return:
        """
        if self.user_os == 'nt':
            email = \
            subprocess.check_output(['whoami', '/upn'], shell=True, universal_newlines=True, encoding='cp850').split(
                '\n')[0]

            return email

        return None

    def _get_user_fqdn(self) -> str | None:
        """
        Permet de récupérer le FQDN de l'utilisateur du le domaine de l'entreprise

        :return:
        """
        if self.user_os == 'nt':
            try:
                fqdn = subprocess.check_output(['whoami', '/fqdn'], shell=True, stderr=subprocess.PIPE,
                                               universal_newlines=True, encoding='cp850').split('\n')[0]

                return fqdn

            except subprocess.CalledProcessError as e:
                self._log(e.stderr, Qgis.Warning)

        return None

    def _get_user_zone(self) -> str | None:
        """
        Permet de définir la zone de l'utilisateur par rapport aux domaines trouvés et aux correspondances indiquées dans la config globale

        :return:
        """
        mail_domain = self.user_email.split('@')[-1]

        fqdn_regex = self._config.get("fqdn_regex", "")
        fqdn_domain = None
        if fqdn_regex and self.user_fqdn:
            search_result = re.search(fqdn_regex, self.user_fqdn)
            if search_result:
                fqdn_domain = search_result.group(1)

        zones = self._config.get("zones", [])

        user_zone = None
        for zone in zones:
            if (
                    self.user_domain == zone.get("domain_ntlm", "") or
                    mail_domain == zone.get("domain_email", "") or
                    fqdn_domain == zone.get("domain_fqdn", "")
            ):
                user_zone = zone.get("name", "")
                break

        if not user_zone:
            self._log(self._tr("Impossible d'identifier la zone de l'utilisateur avec le domaine utilisateur '{}' ou le domaine mail '{}' ou le domaine FQDN '{}'").format(self.user_domain, mail_domain, fqdn_domain), Qgis.Warning)

        self._log(self._tr("Zone de l'utilisateur: {}").format(user_zone), Qgis.Info)

        return user_zone

    def _get_user_role(self) -> str | None:

        if not self.user_d_env or not self.user_zone:
            return None

        role_url = format_str(self._config.get("role_url", ''), self.user_d_env_suffix, self.user_zone)

        if role_url:
            try:
                url = QUrl(role_url)
                query = QUrlQuery()
                query.addQueryItem("user_mail", self.user_email)
                url.setQuery(query)

                role_json = self._request.get_json(url)

            except Exception as e:
                self._log(self._tr("Erreur lors de la lecture du rôle de l'utilisateur: {}").format(str(e)), Qgis.Warning)
                return None

            role = role_json.get("role", None)

            self._log(self._tr("Role de l'utilisateur : {}").format(role), Qgis.Info)

            return role

        return None

    #TODO Identifier les groupes de l'utilisateur "whoami /groups"

    def is_in_scope(self, feature_cfg: dict) -> bool:
        """
        Permet de vérifier si l'utilisateur est concerné par le paramétrage à réaliser

        :param feature_cfg:
        :return:
        """

        f_cfg_zones = [x.lower() for x in feature_cfg.get("zones", ["all"])]
        f_cfg_users = [x.lower() for x in feature_cfg.get("users", [])]
        f_cfg_envs = [x.lower() for x in feature_cfg.get("envs", ["all"])]
        f_cfg_roles = [x.lower() for x in feature_cfg.get("roles", ["all"])]

        # Test sur la zone
        in_zones = False
        if self.user_zone in f_cfg_zones or "all" in f_cfg_zones:
            in_zones = True

        # Test sur le username
        # 'all' n'est pas adapté car le résultat serait toujours True pour la fonction.
        # Ce test est distinct de celui sur le role et la zone
        in_users = False
        if self.user_name in f_cfg_users:
            in_users = True

        # Test sur le role
        in_roles = False
        for role in f_cfg_roles:
            if "all" in f_cfg_roles or (self.user_role and role in self.user_role):
                in_roles = True
                break

        # Test sur l'environnement
        if "all" in f_cfg_envs or (self.user_d_env and self.user_d_env in f_cfg_envs):
            in_d_envs = True
        else:
            in_d_envs = False

        # Si l'environnement n'est pas le bon, le paramétrage n'est pas appliqué
        if not in_d_envs:
            return False

        # Si l'utilisateur est explicitement nommé : Ok
        if in_users:
            return True

        # Si la zone et le role correspondent : Ok
        if in_zones and in_roles:
            return True

        return False
