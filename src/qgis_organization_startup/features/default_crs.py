from qgis.core import QgsSettings

from qgis_organization_startup.common.base import BaseStartup


class CheckDefaultCrs(BaseStartup):
    @BaseStartup.template_function(
        "default_crs",
        "Paramétrage du système de projection par défaut"
    )
    def check(self) -> None:
        default_crs = self._cfg.get("default_crs", "EPSG:4326")

        s = QgsSettings()
        s.setValue("Projections/layerDefaultCrs", default_crs)
        s.setValue("app/projections/defaultProjectCrs", default_crs)
        s.setValue("app/projections/unknownCrsBehavior", "UseDefaultCrs")
        s.setValue("app/projections/newProjectCrsBehavior", "UsePresetCrs")
        s.setValue("app/projections/crsAccuracyWarningThreshold", 0.0)