from route_mapping.modules.qgis.mapFunctions.smoothLine import SmoothLine
from route_mapping.modules.qgis.mapFunctions.closeLine import CloseLine
from route_mapping.modules.qgis.mapFunctions.trimLine import TrimLine
from route_mapping.modules.qgis.mapFunctions.expandLine import ExpandLine
from route_mapping.modules.qgis.mapFunctions.createNewMapView import CreateNewMapView
from route_mapping.modules.qgis.mapFunctions.convergencePoint import ConvergencePoint
from route_mapping.modules.qgis.mapFunctions.createRelationship import CreateRelationship
from route_mapping.modules.qgis.mapFunctions.buildRoute import BuildRoute

class MapFunctionsFactory:

    def getFunction(self, functionName):
        functionNames = {
            'SmoothLine':  SmoothLine,
            'CloseLine':  CloseLine,
            'TrimLine':  TrimLine,
            'ExpandLine':  ExpandLine,
            'CreateNewMapView': CreateNewMapView,
            'ConvergencePoint': ConvergencePoint,
            'CreateRelationship': CreateRelationship,
            'BuildRoute': BuildRoute,
        }
        return functionNames[functionName]()