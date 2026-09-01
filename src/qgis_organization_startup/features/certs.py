import os
import tempfile

from qgis.core import Qgis, QgsAuthCertUtils
from qgis.PyQt.QtNetwork import QSslCertificate
from qgis.PyQt.QtCore import QUrl

from qgis_organization_startup.common.base import BaseStartup


class CheckCerts(BaseStartup):

    @BaseStartup.template_function(
        "certificates",
        "Import de certificats ..."
    )
    def check(self) -> None:
        cert_url = self._cfg.get("cert_url", "")
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Télécharger le certificat
            cert_filename = os.path.basename(cert_url)
            cert_path = os.path.join(tmpdirname, cert_filename)

            url = QUrl(cert_url)

            try:
                r = self._request.get(url)

                with open(cert_path, "wb") as f:
                    f.write(r.content())

            except Exception as e:
                self._log(self._tr("Erreur lors de la lecture du certificat {}: {}".format(cert_url, str(e))), Qgis.Critical)
                return None

            # Charger le certificat
            cert = QgsAuthCertUtils.certFromFile(cert_path)

            # Identifier le Subject Display Name
            sdn = cert.subjectDisplayName()

            # Vérification de l'existance du certificat
            existing_sys_certs = self._a_mgr.systemRootCAs()

            need_cert = True
            for s_cert in existing_sys_certs:
                sdn_s_cert = s_cert.subjectDisplayName()
                if sdn_s_cert == sdn:

                    self._log(self._tr("Le certificat '{}' existe déjà dans le système").format(sdn), Qgis.Info)

                    if not QgsAuthCertUtils.certIsViable(s_cert):
                        self._log(self._tr("Le certificat '{}' existant n'est pas valide et sera remplacé").format(sdn), Qgis.Info)

                    else:
                        need_cert = False

                    break

            if need_cert:
                self._log(self._tr("Ajout/Remplacement du certificat '{}' dans QGIS").format(sdn), Qgis.Info)
                self._add_cert(cert)

            return None

    def _add_cert(self, cert: QSslCertificate) -> None:
        # Ajouter un certificat à QGIS
        sdn = cert.subjectDisplayName()
        if QgsAuthCertUtils.certIsViable(cert):
            self._a_mgr.storeCertAuthority(cert)
            self._log(self._tr("Certificat '{}' ajouté/actualisé").format(sdn), Qgis.Info)
        else:
            self._log(self._tr("Le certificat '{}' n'est pas viable pour QGIS").format(sdn), Qgis.Warning)