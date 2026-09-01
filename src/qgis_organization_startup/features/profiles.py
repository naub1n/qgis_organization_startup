from qgis.core import Qgis

from qgis_organization_startup.common.base import BaseStartup

class CheckProfiles(BaseStartup):

    @BaseStartup.template_function(
        "profiles",
        "Vérification des profiles"
    )
    def check(self) -> None:
        """
        Lance le test sur les profils

        :return:
        """

        e_profiles = self._cfg.get("names", [])

        c_profile = self._p_mgr.userProfile().name()

        if c_profile not in e_profiles:
            self._error(self._tr("Le profil utilisé n'est pas administré par les équipes techniques"))

        for profile in e_profiles:
            if not self._p_mgr.profileExists(profile):
                self._log(self._tr("Création du profil {}").format(profile), Qgis.Info)
                self._p_mgr.createUserProfile(profile)

        d_profile = self._cfg.get("default", "")
        if d_profile:
            self._log(self._tr("{} devient le profil par défaut").format(d_profile), Qgis.Info)
            self._p_mgr.setDefaultProfileName(d_profile)

        sp_profile = self._cfg.get("policy", None)
        if sp_profile:
            self._log(self._tr("La politique de sélection de profil au démarrage est fixée à {}").format(str(sp_profile)), Qgis.Info)
            self._p_mgr.setUserProfileSelectionPolicy(Qgis.UserProfileSelectionPolicy(sp_profile))

        return None
