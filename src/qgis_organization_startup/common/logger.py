from qgis.core import QgsMessageLog, Qgis

class StartupLogger:
    def __init__(self, tag: str, raise_on_error: bool = False):
        """

        :param tag: Nom de l'onglet dans le journal des messages de QGIS
        :param raise_on_error: Indique si python déclenche une exception lors d'une erreur
        """
        self.tag = tag
        self.raise_on_error = raise_on_error

    def log(self, log_message: str, log_level: Qgis.MessageLevel) -> None:
        """
        Ajoute un message à l'onglet dédié dans le journal des messages de QGIS

        :param log_message: Message
        :param log_level: Niveau de log
        :return:
        """
        QgsMessageLog.logMessage(log_message, self.tag, level=log_level, notifyUser=False)

    def error(self, log_message: str) -> None:
        if self.raise_on_error:
            raise Exception(log_message)
        else:
            self.log(log_message, Qgis.Critical)