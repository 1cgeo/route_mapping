from qgis.utils import iface
from qgis import gui, core
from qgis.PyQt.Qt import QVariant
from qgis.core import QgsGeometry, QgsPoint
import math
from route_mapping.modules.qgis.mapFunctions.mapFunction import MapFunction
from route_mapping.modules.database.factories.databaseFactory import DatabaseFactory

from PyQt5 import QtWidgets, QtCore
from functools import wraps

def waitingcursor(func):
    @wraps(func)
    def inner(*args, **kwargs):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            return func(*args)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()            
    return inner


class BuildRouteStructure(MapFunction):

    def __init__(self,
            databaseFactory=DatabaseFactory()
        ):
        super(BuildRouteStructure, self).__init__()
        self.databaseFactory = databaseFactory

    @waitingcursor
    def run(self,
            routeSchema,
            routeTable,
            edgeSchema,
            edgeTable,
            dbName,
            dbHost,
            dbPort,
            dbUser,
            dbPass
        ):
        srid = iface.mapCanvas().mapSettings().destinationCrs().postgisSrid()
        database = self.databaseFactory.createPostgres(
            dbName,
            dbHost,
            dbPort,
            dbUser,
            dbPass,
        )
        return database.buildRouteStructure(
            routeSchema,
            routeTable,
            edgeSchema,
            edgeTable
        )
      
        

       
        


