import subprocess

from abc import abstractmethod
from functools import wraps
from qgis.core import Qgis, QgsApplication
from qgis.utils import iface

from qgis_organization_startup.common.profiler import StartupProfiler
from qgis_organization_startup.common.min_base import MinBaseStartup
from qgis_organization_startup.common.user import UserInfo
from qgis_organization_startup.common.format_str import format_str
from qgis_organization_startup.common.logger import StartupLogger

class BaseStartup(MinBaseStartup):
    def __init__(self, config: dict, user_info: UserInfo, logger: StartupLogger, profiler: StartupProfiler):
        super().__init__(config, logger)

        self._user = user_info
        self.logger = logger
        self._sp = profiler

        self._p_mgr = iface.userProfileManager()
        self._a_mgr = QgsApplication.authManager()

        # Initialisation de la variable contenant le paramétrage unitaire
        self._cfg: dict = {}

    def _format(self, value: str | None) -> str | None:
        new_value = format_str(value, self._user.user_d_env_suffix, self._user.user_zone)

        return new_value

    @abstractmethod
    def check(self) -> None:
        pass

    @staticmethod
    def template_function(f_key: str, title: str):
        """
        Fonction template à réutiliser dans les différentes fonctionnalités de vérification du paramétrage

        :param f_key: Clé de la config dans le fichier json de paramétrage
        :param title: Titre utilisé dans les logs
        :return:
        """

        def decorator(func):

            @wraps(func)
            def wrapper(self, *args, **kwargs) -> bool:
                p_name = self._tr(title)
                self._log(p_name, Qgis.Info)
                self._sp.start(p_name)

                success = False

                try:
                    f_config = self._config.get(f_key, [])

                    for cfg in f_config:
                        if self._user.is_in_scope(cfg):
                            self._cfg = cfg
                            func(self, *args, **kwargs)

                    success = True

                except Exception as e:
                    self.logger.error(self._tr("Erreur lors du paramétrage : {}").format(str(e)))

                self._sp.end()

                return success

            return wrapper

        return decorator

    def powershell_cmd(self, command: str) -> subprocess.CompletedProcess[str]:
        ps_exe = 'C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe'
        cmd_result = subprocess.run(ps_exe + " -Command " + command, shell=True, capture_output=True, text=True,
                                    universal_newlines=True, encoding='cp850')

        return cmd_result


class BasePluginSetup(BaseStartup):

    def check(self) -> None:
        pass

    @abstractmethod
    def setup(self, plugin_config: dict) -> None:
        pass

    @staticmethod
    def template_setup(plugin_name: str):
        """
        Fonction template à réutiliser dans le paramétrage des plugins

        :param plugin_name: Nom du plugin
        :return:
        """

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs) -> None:
                p_name = self._tr("Paramétrage du plugin {}").format(plugin_name)
                self._log(p_name, Qgis.Info)
                self._sp.start(p_name)

                func(self, *args, **kwargs)

                self._sp.end()

            return wrapper

        return decorator
