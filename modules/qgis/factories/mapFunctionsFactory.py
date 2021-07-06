from route_mapping.modules.qgis.mapFunctions.createRelationship import CreateRelationship
from route_mapping.modules.qgis.mapFunctions.buildRoute import BuildRoute
from route_mapping.modules.qgis.mapFunctions.buildRouteStructure import BuildRouteStructure
from route_mapping.modules.qgis.mapFunctions.loadLayer import LoadLayer
from route_mapping.modules.qgis.mapFunctions.buildRouteWithoutRestriction import BuildRouteWithoutRestriction

class MapFunctionsFactory:

    def getFunction(self, functionName):
        functionNames = {
            'CreateRelationship': CreateRelationship,
            'BuildRoute': BuildRoute,
            'BuildRouteWithoutRestriction': BuildRouteWithoutRestriction,
            'BuildRouteStructure': BuildRouteStructure,
            'LoadLayer': LoadLayer
        }
        return functionNames[functionName]()