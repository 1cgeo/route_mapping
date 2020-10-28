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
            routeTable,
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
            vehicle
        )
        self.isValidRoute(route)
        valueMaps = database.getAttributeValueMap(routeTable, routeSchema)
        self.exportToMemoryLayer(
            route, 
            srid,
            valueMaps
        )
        return route

    def isValidRoute(self, route):
        for step in route:
            if not(int(step['cost']) >= 10000):
                continue
            raise Exception("Route not found")

    def exportToMemoryLayer(self, route, srid, valueMaps):
        vectorLyr =  core.QgsVectorLayer(
            'LineString?crs=epsg:{0}{1}'.format(srid, self.getMemoryLayerFieldsUrl()), 'rota' , "memory"
        )
        vl = core.QgsProject().instance().addMapLayer(vectorLyr)
        vl.startEditing()
        feat = core.QgsFeature(vl.fields())
        pavingValueMap = [ valueMap for valueMap in valueMaps if valueMap['attribute'] == 'tipopavimentacao']
        pavingValueMap = pavingValueMap[0]['valueMap'] if pavingValueMap else {}
        getPavingValue = lambda code, valueMap=pavingValueMap: list(pavingValueMap.keys())[list(pavingValueMap.values()).index(code)]
        for step in route:
            step['paving'] = getPavingValue(step['paving']).split('(')[0].strip()
            feat.setAttribute('id', step['seq'])
            feat.setAttribute('nome', step['name'])
            feat.setAttribute('sigla', step['initials'])
            feat.setAttribute('pavimentacao', step['paving'])
            feat.setAttribute('faixas', step['tracks'])
            feat.setAttribute('velocidade', step['velocity'])
            feat.setAttribute('observacao', step['note'])
            feat.setGeometry(QgsGeometry.fromWkt(step['wkt']))
            vl.addFeature(feat)
        vl.commitChanges()

    def getMemoryLayerFieldsUrl(self):
        fields = [
            ('id', 'int'),
            ('nome', 'string'),
            ('sigla', 'string'),
            ('pavimentacao', 'string'),
            ('faixas', 'string'),
            ('velocidade', 'double'),
            ('observacao', 'string')
        ]
        return '&field='+'&field='.join([ '{0}:{1}'.format(row[0], row[1]) for row in fields])


        

       
        


