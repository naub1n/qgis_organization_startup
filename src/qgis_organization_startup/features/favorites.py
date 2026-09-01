from qgis.core import Qgis, QgsFavoritesItem

from qgis_organization_startup.common.base import BaseStartup


class CheckFavorites(BaseStartup):

    @BaseStartup.template_function(
        "favorites",
        "Vérification des marques-pages"
    )
    def check(self) -> None:
        f_path = self._cfg.get("path", "")
        f_name = self._cfg.get("name", f_path)

        fi = QgsFavoritesItem(None, "")

        # Vérification de la présence du marque-page
        for item in fi.createChildren():
            if item.name() == f_name:
                fi.removeDirectory(item)

        self._log(self._tr("Ajout/Restauration du marque-page '{}'.").format(f_path), Qgis.Info)
        fi.addDirectory(f_path, f_name)
