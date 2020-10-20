from qgis.utils import iface
from qgis import gui, core
from qgis.PyQt.Qt import QVariant
from qgis.core import QgsGeometry, QgsPoint
import math
from route_mapping.modules.qgis.mapFunctions.mapFunction import MapFunction
from route_mapping.modules.database.factories.databaseFactory import DatabaseFactory

class BuildRoute(MapFunction):

    def __init__(self,
            databaseFactory=DatabaseFactory()
        ):
        super(BuildRoute, self).__init__()
        self.databaseFactory = databaseFactory

    def run(self, 
            sourceX,
            sourceY,
            targetX,
            targetY,
            edgeSchema,
            edgeTable,
            restrictionSchema,
            restrictionTable,
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
        sourcetId, sourcePos = database.getNearestRoutingPoint(
            sourceX,
            sourceY,
            srid,
            edgeSchema,
            edgeTable
        )
        targetId, targetPos = database.getNearestRoutingPoint(
            targetX,
            targetY,
            srid,
            edgeSchema,
            edgeTable
        )
        route = database.getRoute(
            sourcetId, 
            sourcePos,
            targetId, 
            targetPos,
            srid,
            edgeSchema,
            edgeTable,
            restrictionSchema,
            restrictionTable,
            (sourceX, sourceY),
            (targetX, targetY)
        )
        self.exportToMemoryLayer(route, srid)
        return route

    def exportToMemoryLayer(self, route, srid):
        vectorLyr =  core.QgsVectorLayer('LineString?crs=epsg:{0}&field=id:int'.format(srid), 'rota' , "memory")
        vl = core.QgsProject().instance().addMapLayer(vectorLyr)
        vl.startEditing()
        feat = core.QgsFeature(vl.fields())
        for step in route:
            feat.setAttribute('id', step[0])
            feat.setGeometry(QgsGeometry.fromWkt(step[-1]))
            vl.addFeature(feat)
        vl.commitChanges()

        

       
        


