import subprocess
import time
import win32com.client

from qgis_organization_startup.common.base import BaseStartup

class CheckNetworkDrives(BaseStartup):

    @BaseStartup.template_function(
        f_key="network_drives",
        title="Ouverture des lecteurs réseau pour les activer"
    )
    def check(self) -> None:
        """
        Lance le test sur le lecteur réseau (Windows uniquement)

        :return:
        """
        drives = self._cfg.get("drives", []) # _cfg
        for d in drives:
            subprocess.run(["start", "/min", "explorer", "%s" % d], shell=True)
            time.sleep(2)
            self._close_explorer_window(d)

    def _close_explorer_window(self, target_path):
        """
        Ferme les fenêtres ouvertes avec l'exportateur Windows

        :param target_path: Chemin indiqué dans la fenêtre de l'explorateur
        :return:
        """
        shell = win32com.client.Dispatch("Shell.Application")
        windows = shell.Windows()
        for window in windows:
            try:
                if window.Document.Folder.Self.Path == target_path:
                    window.Quit()
            except Exception as e:
                pass