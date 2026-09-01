from qgis.core import QgsApplication

class StartupProfiler:
    def __init__(self, group_name: str):
        self._profiler = QgsApplication.profiler()
        self._group_name = group_name

    def start(self, name: str):
        """
        Démarre le monitoring du processus nommé

        :param name: Nom du processus
        :return:
        """

        self._profiler.start(name, self._group_name)

    def end(self):
        """
        Arrête le dernier monitoring lancé

        :return:
        """
        self._profiler.end(self._group_name)