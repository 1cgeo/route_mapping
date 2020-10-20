from route_mapping.modules.qgis.mapFunctions.createRelationship import CreateRelationship
from route_mapping.modules.qgis.mapFunctions.buildRoute import BuildRoute
from route_mapping.modules.qgis.mapFunctions.buildRouteStructure import BuildRouteStructure

class MapFunctionsFactory:

    def getFunction(self, functionName):
        functionNames = {
            'CreateRelationship': CreateRelationship,
            'BuildRoute': BuildRoute,
            'BuildRouteStructure': BuildRouteStructure 
        }
        return functionNames[functionName]()