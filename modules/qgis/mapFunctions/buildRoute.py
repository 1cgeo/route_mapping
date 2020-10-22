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
            sourcePoint,
            targetPoint,
            routeSchema,
            restrictionSchema,
            restrictionTable,
            dbConnection,
            vehicle
        ):
        srid = iface.mapCanvas().mapSettings().destinationCrs().postgisSrid()
        database = self.databaseFactory.createPostgres(*dbConnection)
        sourcePointEdgeInfo = database.getNearestRoutingPoint(
            sourcePoint,
            srid,
            routeSchema
        )
        targetPointEdgeInfo = database.getNearestRoutingPoint(
            targetPoint,
            srid,
            routeSchema
        )
        route = database.getRoute(
            sourcePointEdgeInfo,
            targetPointEdgeInfo,
            srid,
            routeSchema,
            restrictionSchema,
            restrictionTable,
            sourcePoint,
            targetPoint,
            vehicle
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

        

       
        


