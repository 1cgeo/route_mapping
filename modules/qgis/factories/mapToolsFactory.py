from route_mapping.modules.qgis.factories.trimLineMapToolSingleton import TrimLineMapToolSingleton
from route_mapping.modules.qgis.factories.expandLineMapToolSingleton import ExpandLineMapToolSingleton
from route_mapping.modules.qgis.factories.convergencePointMapToolSingleton import ConvergencePointMapToolSingleton
from route_mapping.modules.qgis.factories.createRelationshipMapToolSingleton import CreateRelationshipMapToolSingleton
from route_mapping.modules.qgis.factories.getClickCoordinatesSingleton import GetClickCoordinatesSingleton
from route_mapping.modules.qgis.mapTools.getClickCoordinates import GetClickCoordinates

class MapToolsFactory:

    def getTool(self, toolName):
        toolNames = {
            'TrimLineMapTool':  lambda: TrimLineMapToolSingleton.getInstance(),
            'ExpandLineMapTool':  lambda: ExpandLineMapToolSingleton.getInstance(),
            'ConvergencePoint': lambda: ConvergencePointMapToolSingleton.getInstance(),
            'CreateRelationship': lambda: CreateRelationshipMapToolSingleton.getInstance(),
            'GetClickCoordinates': GetClickCoordinates
        }
        return toolNames[toolName]()