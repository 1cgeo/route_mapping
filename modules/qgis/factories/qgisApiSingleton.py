from route_mapping.modules.qgis.api.qgisApi import QgisApi

class QgisApiSingleton:

    qgisApi = None

    @staticmethod
    def getInstance():
        if not QgisApiSingleton.qgisApi:
            QgisApiSingleton.qgisApi = QgisApi()
        return QgisApiSingleton.qgisApi