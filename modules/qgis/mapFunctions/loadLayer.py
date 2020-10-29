from qgis.utils import iface
from qgis import gui, core
from qgis.PyQt.Qt import QVariant
from qgis.core import QgsGeometry, QgsPoint
import math
from route_mapping.modules.qgis.mapFunctions.mapFunction import MapFunction

class LoadLayer(MapFunction):

    def __init__(self):
        super(LoadLayer, self).__init__()

    def run(self, 
            dbSchema, 
            dbTable,
            dbName, 
            dbHost, 
            dbPort, 
            dbUser, 
            dbPassword,
            isGeom,
            qmlStyle=''
        ):
        lyr = self.loadPostgresLayer(
            dbName, 
            dbHost, 
            dbPort, 
            dbUser, 
            dbPassword, 
            dbSchema, 
            dbTable,
            isGeom=isGeom
        )
        if qmlStyle:
            self.setQmlStyleToLayer(lyr, qmlStyle)
        return lyr

    def getUri(self, 
            dbName, 
            dbHost, 
            dbPort, 
            dbUser, 
            dbPassword, 
            dbSchema, 
            dbTable,
            isGeom
        ):
        return u"""dbname='{}' host={} port={} user='{}' password='{}' key='id' table="{}"."{}" {} sql= """.format(
            dbName, 
            dbHost, 
            dbPort, 
            dbUser,
            dbPassword,
            dbSchema,
            dbTable,
            '(geom)' if isGeom else ''
        )

    def loadPostgresLayer(self, 
                dbName, 
                dbHost, 
                dbPort, 
                dbUser, 
                dbPassword, 
                dbSchema, 
                dbTable, 
                groupParent=None,
                isGeom=True
            ):
        lyr = core.QgsVectorLayer(
            self.getUri(
                dbName, 
                dbHost, 
                dbPort, 
                dbUser, 
                dbPassword, 
                dbSchema, 
                dbTable, 
                isGeom
            ), 
            dbTable, 
            u"postgres"
        )
        if groupParent is None:
            return core.QgsProject.instance().addMapLayer(lyr)
        layer = core.QgsProject.instance().addMapLayer(lyr, False)
        groupParent.addLayer(layer)
        return layer

       
        


