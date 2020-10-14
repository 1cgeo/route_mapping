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

    def run(self, points, routeSettings):
        srid = iface.mapCanvas().mapSettings().destinationCrs().postgisSrid()
        database = self.databaseFactory.createPostgres(
            routeSettings['dbName'], 
            routeSettings['dbHost'], 
            routeSettings['dbPort'], 
            routeSettings['dbUser'], 
            routeSettings['dbPass']
        )
        sourceInfo = database.getNearestRoutingPoint(
            points['source']['x'],
            points['source']['y'],
            srid,
            routeSettings['schemaRoute'],
            routeSettings['tableRoute']
        )
        targetInfo = database.getNearestRoutingPoint(
            points['target']['x'],
            points['target']['y'],
            srid,
            routeSettings['schemaRoute'],
            routeSettings['tableRoute']
        )
        routeWkt = database.getRouteWkt(
            sourceInfo['edgeId'],
            sourceInfo['edgePos'],
            targetInfo['edgeId'],
            targetInfo['edgePos'],
            srid,
            routeSettings['schemaRoute'],
            routeSettings['tableRoute'],
            routeSettings['schemaRestriction'],
            routeSettings['tableRestriction']
        )
        """ print(QgsGeometry.fromWkt(routeWkt))
        return
        qgsPoints = [self.createPointFromWkt(sourceInfo['edgePoint'])]
        [ qgsPoints.append(self.createPointFromWkt(item[2])) for item in routePoints if item[2] ]
        qgsPoints.append(self.createPointFromWkt(targetInfo['edgePoint'])) """
        self.exportToMemoryLayer(QgsGeometry.fromWkt(routeWkt), srid)

    def createPointFromWkt(self, wkt):
        p = QgsPoint()
        p.fromWkt(wkt)
        return p

    def exportToMemoryLayer(self, geometry, srid):
        vectorLyr =  core.QgsVectorLayer('LineString?crs=epsg:{0}&field=id:int'.format(srid), 'rota' , "memory")
        vl = core.QgsProject().instance().addMapLayer(vectorLyr)
        vl.startEditing()
        feat = core.QgsFeature(vl.fields())
        feat.setGeometry(geometry)
        vl.addFeature(feat)
        vl.commitChanges()

        

       
        


