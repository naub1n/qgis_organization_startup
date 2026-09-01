from qgis.core import Qgis, QgsApplication, QgsColorScheme
from qgis.PyQt.QtGui import QColor

from qgis_organization_startup.common.base import BaseStartup


class CheckColors(BaseStartup):

    @BaseStartup.template_function(
        "color_schemes",
        "Ajout des schémas de couleurs"
    )
    def check(self) -> None:
        cs_name = self._cfg.get("name", "")
        cs_colors = self._cfg.get("colors", [])

        self._log(self._tr("Ajout du schéma de couleurs {}").format(cs_name), Qgis.Info)

        new_color_scheme = NewColorScheme(name=cs_name, json_colors=cs_colors)
        csr = QgsApplication.colorSchemeRegistry()
        csr.addColorScheme(new_color_scheme)

class NewColorScheme(QgsColorScheme):
    def __init__(self, parent=None, name="", json_colors=[]):
        QgsColorScheme.__init__(self)
        self.name = name
        self.colors = json_colors

    def schemeName(self):
        return self.name

    def fetchColors(self, context='', basecolor=QColor()):
        new_colors = []
        for color in self.colors:
            new_color = []
            new_color.append(QColor(color.get("code", "#FFFFFF")))
            new_color.append(color.get("name", "unknown"))

            new_colors.append(new_color)

        return new_colors

    def flags(self):
        return QgsColorScheme.ShowInAllContexts

    def clone(self):
        return NewColorScheme()