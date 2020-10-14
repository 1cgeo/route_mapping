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
        sourcePoint = self.createPointFromWkt(sourceInfo['edgePoint'])
        targetPoint = self.createPointFromWkt(targetInfo['edgePoint'])
        xmin, ymin, xmax, ymax = self.getXYMaxMinFromPoints(sourcePoint, targetPoint)
        routeWkt = database.getRouteWkt(
            sourceInfo['edgeId'],
            sourceInfo['edgePos'],
            targetInfo['edgeId'],
            targetInfo['edgePos'],
            srid,
            routeSettings['schemaRoute'],
            routeSettings['tableRoute'],
            routeSettings['schemaRestriction'],
            routeSettings['tableRestriction'],
            (points['source']['x'], points['source']['y']),
            (points['target']['x'], points['target']['y'])
        )
        self.exportToMemoryLayer(QgsGeometry.fromWkt(routeWkt), srid)

    def createPointFromWkt(self, wkt):
        p = QgsPoint()
        p.fromWkt(wkt)
        return p

    def getXYMaxMinFromPoints(self, p1, p2):
        xmin = p1.x()
        xmax = p1.x()
        if p2.x() > p1.x():
            xmax = p2.x()
        else:
            xmin = p2.x()
        ymin = p1.y()
        ymax = p1.y()
        if p2.y() > p1.y():
            ymax = p2.y()
        else:
            ymin = p2.y()
        return xmin, ymin, xmax, ymax

    def exportToMemoryLayer(self, geometry, srid):
        vectorLyr =  core.QgsVectorLayer('LineString?crs=epsg:{0}&field=id:int'.format(srid), 'rota' , "memory")
        vl = core.QgsProject().instance().addMapLayer(vectorLyr)
        vl.startEditing()
        feat = core.QgsFeature(vl.fields())
        feat.setGeometry(geometry)
        vl.addFeature(feat)
        vl.commitChanges()

        

       
        


