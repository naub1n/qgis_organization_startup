from .version import CheckVersion
from .profiles import CheckProfiles
from .env_var import CheckEnvVar
from .network_drives import CheckNetworkDrives
from .certs import CheckCerts
from .repos import CheckRepositories
from .auth_configs import CheckAuthConfigs
from .plugins import CheckPlugins, CheckPluginsConfigs
from .db_connections import CheckDbConnections
from .favorites import CheckFavorites
from .wfs_connections import CheckWFSConnections
from .wms_connections import CheckWMSConnections
from .arcgis_connections import CheckArcgisConnections
from .svg_paths import CheckSVGPaths
from .layout_templates import CheckLayoutTemplates
from .qgis_settings import CheckQGISSettings
from .colors import CheckColors
from .pgservices import CheckPGServices
from .listener_session_role import CheckListenerSessionRole

ALL_FEATURES = [
    CheckVersion, # A mettre en première place
    CheckProfiles, # A mettre en seconde place
    CheckEnvVar,
    CheckNetworkDrives,
    CheckCerts,
    CheckRepositories,
    CheckAuthConfigs,
    CheckPlugins,
    CheckPluginsConfigs,
    CheckDbConnections,
    CheckFavorites,
    CheckWFSConnections,
    CheckWMSConnections,
    CheckArcgisConnections,
    CheckSVGPaths,
    CheckLayoutTemplates,
    CheckQGISSettings,
    CheckColors,
    CheckPGServices,
    CheckListenerSessionRole
]
