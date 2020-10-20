from route_mapping.modules.qgis.factories.createRelationshipMapToolSingleton import CreateRelationshipMapToolSingleton
from route_mapping.modules.qgis.mapTools.getClickCoordinates import GetClickCoordinates

class MapToolsFactory:

    def getTool(self, toolName):
        toolNames = {
            'CreateRelationship': lambda: CreateRelationshipMapToolSingleton.getInstance(),
            'GetClickCoordinates': GetClickCoordinates
        }
        return toolNames[toolName]()