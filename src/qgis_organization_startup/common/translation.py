import gettext

from qgis.core import QgsApplication
from importlib.resources import files

def gettext_tr():
    locale_dir = str(
        files("qgis_organization_startup").joinpath("locales")
    )
    domain = "messages"

    gettext.bindtextdomain(domain, locale_dir)
    gettext.textdomain(domain)

    current_language = QgsApplication.locale()

    translation = gettext.translation(domain, locale_dir, languages=[current_language], fallback=True)
    translation.install()

    return translation.gettext
