import os
import subprocess
import json

from qgis.PyQt import QtWidgets
from qgis.PyQt.QtCore import Qt
from qgis.core import Qgis, QgsAuthMethodConfig

from qgis_organization_startup.common.base import BaseStartup


class CheckAuthConfigs(BaseStartup):

    @BaseStartup.template_function(
        "authentications",
        "Vérification des configurations d'authentification"
    )
    def check(self) -> None:
        """
        Permet de lancer le test sur les configurations d'authentification et de vérifier le mot de passe principal de QGIS

        :return:
        """

        # Vérification préalable du mot de passe principal de QGIS
        self._check_master_pass()

        auth_id = self._cfg.get("id", "")
        auth_name = self._cfg.get("name", "")
        auth_user = self._cfg.get("user", "")
        auth_pass = self._cfg.get("pass", "")
        auth_type = self._cfg.get("type", "")
        auth_is_enterprise_auth = self._cfg.get("is_enterprise_auth", False)
        auth_request_url = self._cfg.get("request_url", "")
        auth_token_url = self._cfg.get("token_url", "")
        auth_client_id = self._cfg.get("client_id", "")
        auth_client_secret = self._cfg.get("client_secret", "")
        auth_scope = self._cfg.get("scope", "")
        auth_apikey = self._cfg.get("apikey", "")
        auth_force_refresh = self._cfg.get("force_refresh", False)
        auth_force_empty = self._cfg.get("force_empty", False)

        ids = self._a_mgr.availableAuthMethodConfigs().keys()

        if auth_id in ids and not auth_force_refresh:
            self._log(self._tr("La configuration {} est déjà présente").format(str(auth_id)), Qgis.Info)

        else:
            self._log(self._tr("Ajout de la configuration d'authentification {}").format(str(auth_id)), Qgis.Info)

            if auth_is_enterprise_auth:
                if not self._check_enterprise_pass(auth_id, auth_name):
                    return

            if (auth_user and auth_pass) or (auth_user and auth_force_empty) or auth_type == 'OAuth2':
                self._save_auth_config(
                    auth_id=auth_id,
                    name=auth_name,
                    user=auth_user,
                    password=auth_pass,
                    client_id=auth_client_id,
                    client_secret=auth_client_secret,
                    req_url=auth_request_url,
                    token_url=auth_token_url,
                    scope=auth_scope,
                    method=auth_type
                )

            elif auth_type == 'APIHeader':
                self._save_auth_config(
                    auth_id=auth_id,
                    name=auth_name,
                    apikey=auth_apikey,
                    method=auth_type
                )

    def _check_master_pass(self) -> None:
        verified = self._a_mgr.setMasterPassword(verify=True)

        doc_url = self._format(self._config.get("doc", {}).get("forgot_pass_url", None))

        warn_msg = self._tr("Mot de passe principal non vérifié")

        if not verified:

            if doc_url:
                html_doc_url = '<a href="%s">Mot de passe principal perdu</a>' % doc_url

                mp_alert_dlg = QtWidgets.QDialog(None)
                mp_alert_dlg.setWindowTitle(self._tr("Réinitialiser son mot de passe principal"))

                qt_label = QtWidgets.QLabel(mp_alert_dlg)
                qt_label.setText(
                    self._tr("Si vous ne vous souvenez plus de votre mot de passe principal, veuillez suivre la procédure ci-dessous :")
                )
                qt_url = QtWidgets.QLabel(mp_alert_dlg)
                qt_url.setText(html_doc_url)
                qt_url.setAlignment(Qt.AlignCenter)
                qt_url.setOpenExternalLinks(True)

                button_close = QtWidgets.QPushButton('Fermer', mp_alert_dlg)
                button_close.clicked.connect(lambda: mp_alert_dlg.accept())

                layout = QtWidgets.QVBoxLayout(mp_alert_dlg)
                layout.addWidget(qt_label)
                layout.addWidget(qt_url)
                layout.addWidget(button_close)

                mp_alert_dlg.setLayout(layout)
                mp_alert_dlg.setWindowModality(Qt.WindowModal)
                mp_alert_dlg.exec_()

                warn_msg = "{}. Suivre la procédure : {}".format(warn_msg, html_doc_url)

            self._error(warn_msg)

    def _check_enterprise_pass(self, authcfg_id: str, authcfg_name: str) -> bool:
        """
        Permet de vérifier le mot de passe renseigné en le testant sur l'infrastructure

        :param authcfg_id: ID de la configuration d'authentification
        :param authcfg_name: Nom de la configuration d'authentification
        :return:
        """

        check_result = False
        n_try = 3

        while not check_result and n_try > 0:

            if n_try == 0:
                self._error(self._tr("Vérification du mot de passe de la configuration '{}' impossible après plusieurs tentatives").format(authcfg_id))
                return False

            success, decrypted_config = self._a_mgr.loadAuthenticationConfig(
                authcfg_id,
                QgsAuthMethodConfig(),
                full=True,
            )

            if not success:
                self._change_pass_dlg(self._user.user_email, authcfg_id, authcfg_name)

            if not self._check_domain_connected():
                self._error(self._tr("Vérification du mot de passe de la configuration '{}' impossible car vous ne semblez pas être connecté au domain").format(authcfg_id))
                return False

            auth_cfg = decrypted_config.configMap()

            self._log(self._tr("Vérification du mot de passe de la configuration '{}'").format(authcfg_id), Qgis.Info)
            check_pass_result = False
            if os.name == 'nt':
                check_pass_result = self._check_windows_enterprise_pass(auth_cfg)

            if not auth_cfg.get("password", None) or not check_pass_result:
                self._change_pass_dlg(self._user.user_email, authcfg_id, authcfg_name)

            else:
                check_result = True

        return True

    def _change_pass_dlg(self, username: str, authcfg_id: str, authcfg_name: str) -> None:
        auth_dlg = QtWidgets.QDialog(None)
        auth_dlg.setFixedWidth(450)
        auth_dlg.setWindowTitle(self._tr("Indiquer votre login et mdp"))

        login = QtWidgets.QLineEdit(auth_dlg)
        login.setPlaceholderText(self._tr("Indiquer votre email"))

        if username:
            login.setText(username)

        password = QtWidgets.QLineEdit(auth_dlg)
        password.setEchoMode(QtWidgets.QLineEdit.Password)
        password.setPlaceholderText(self._tr("Indiquer votre mot de passe d'entreprise"))

        qt_title = QtWidgets.QLabel(auth_dlg)
        qt_title.setText(authcfg_name)

        button_save = QtWidgets.QPushButton('Enregistrer', auth_dlg)
        button_save.clicked.connect(
            lambda: self._button_save_clicked(auth_dlg, authcfg_id, authcfg_name, login.text(), password.text()))

        layout = QtWidgets.QVBoxLayout(auth_dlg)
        layout.addWidget(qt_title)
        layout.addWidget(login)
        layout.addWidget(password)
        layout.addWidget(button_save)

        auth_dlg.setLayout(layout)
        auth_dlg.setWindowModality(Qt.WindowModal)
        auth_dlg.exec_()

    def _button_save_clicked(self, auth_dlg: QtWidgets.QDialog, authcfg_id, authcfg_name, authcfg_user, authcfg_pass):
        self._save_auth_config(authcfg_id, authcfg_name, authcfg_user, authcfg_pass)
        auth_dlg.accept()

    def _save_auth_config(self,
                          auth_id: str,
                          name: str,
                          user: str | None = None,
                          password: str | None = None,
                          client_id: str | None = None,
                          client_secret: str | None = None,
                          req_url: str | None = None,
                          token_url: str | None = None,
                          scope: str | None = None,
                          apikey: str | None = None,
                          method: str = "Basic"):

        config = QgsAuthMethodConfig()
        config.setId(auth_id)
        config.setName(name)

        if method == 'Basic':
            config.setConfig('username', user)
            config.setConfig('password', password)
            config.setMethod("Basic")
        elif method == 'OAuth2':
            oauth2_config = {
                "accessMethod": 0,
                "apiKey": "",
                "clientId": client_id,
                "clientSecret": client_secret,
                "configType": 1,
                "customHeader": "",
                "description": "",
                "grantFlow": 0,
                "id": "",
                "name": "",
                "objectName": "",
                "password": "",
                "persistToken": False,
                "queryPairs": {},
                "redirectPort": 7070,
                "redirectUrl": "",
                "refreshTokenUrl": "",
                "requestTimeout": 30,
                "requestUrl": req_url,
                "scope": scope,
                "tokenUrl": token_url,
                "username": "",
                "version": 1
            }

            config_map = {
                'oauth2config': json.dumps(oauth2_config)
            }

            config.setMethod('OAuth2')
            config.setConfigMap(config_map)

        elif method == 'APIHeader':
            config.setConfig('apikey', apikey)
            config.setMethod("APIHeader")

        assert config.isValid()

        self._a_mgr.storeAuthenticationConfig(config, overwrite=True)

    def _check_domain_connected(self) -> bool:
        """
        Permet de vérifier si l'ordinateur est connecté au domaine de l'entreprise

        :return:
        """

        if os.name == 'nt':
            check_cmd = '"(Get-NetConnectionProfile | Where-Object {$_.NetworkCategory -eq \'Domain\'}) -ne $null"'
            cmd_result = self.powershell_cmd(check_cmd)
            check_result = cmd_result.stdout.split('\n')[0].lower() == "true"

            return check_result

        return False

    def _check_windows_enterprise_pass(self, auth_cfg: dict) -> bool:
        """
        Permet de vérifier via prowershell l'authentification renseignée dans la configuration d'authentification de QGIS

        :param auth_cfg: Configuration d'authentification mappée
        :return:
        """
        try:
            check_cmd = '"(new-object directoryservices.directoryentry \'\',\'%s\',\'%s\').psbase.name -ne $null"' % (
                auth_cfg.get("username", None), auth_cfg.get("password", None))
            cmd_result = self.powershell_cmd(check_cmd)
            check_result = cmd_result.stdout.split('\n')[0].lower() == "true"

        except subprocess.CalledProcessError as e:
            self._log(e.stderr, Qgis.Warning)
            check_result = False

        return check_result
