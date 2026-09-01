from qgis.core import QgsApplication

from qgis_organization_startup.common.base import BaseStartup


class CheckSVGPaths(BaseStartup):
    @BaseStartup.template_function(
        "svg_paths",
        "Ajout des symboles SVG"
    )
    def check(self) -> None:
        svg_path = self._cfg.get("path", "")

        qgs_svg_paths = QgsApplication.svgPaths()

        if svg_path not in qgs_svg_paths:
            qgs_svg_paths.append(svg_path)
            QgsApplication.setDefaultSvgPaths(qgs_svg_paths)