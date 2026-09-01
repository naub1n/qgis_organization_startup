import json

from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import QgsNetworkAccessManager, QgsNetworkReplyContent, Qgis

from qgis_organization_startup.common.logger import StartupLogger

class StartupRequest:
    def __init__(self, logger: StartupLogger):
        self._nam = QgsNetworkAccessManager.instance()
        self.logger = logger

    def get(self, url: QUrl) -> QgsNetworkReplyContent:
        req = QNetworkRequest(url)
        reply = self._nam.blockingGet(req)

        return reply

    def get_json(self, url: QUrl) -> dict | None:
        r = self.get(url)

        if not r.error() == QNetworkReply.NoError:
            self.logger.error(r.errorString())
            return {}

        t = bytes(r.content()).decode("utf-8")
        data = json.loads(t)

        return data

    def post(self, url: QUrl, data) -> QgsNetworkReplyContent:
        req = QNetworkRequest(url)
        reply = self._nam.blockingPost(req, data)

        return reply
