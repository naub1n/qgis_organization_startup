from qgis.utils import iface

from qgis_organization_startup.common.min_base import MinBaseStartup

p_mgr = iface.userProfileManager()

class StartupDeployEnv(MinBaseStartup):

    def get_env(self) -> tuple[str | None, str | None]:
        """
        Permet de récupérer l'identifiant de l'environnement de déploiement qui sera utilisé dans les configurations

        :return: Tuple contenant : (Nom de l'environnement, Suffixe de l'environnement)
        """
        profile_name = p_mgr.userProfile().name()
        deploy_envs = self._config.get("deploy_envs", [])

        for env in deploy_envs:
            if profile_name in env.get("profiles", []):
                return env.get("name"), env.get("suffix", None)

        return None, None
