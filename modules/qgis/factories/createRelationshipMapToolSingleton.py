
from route_mapping.modules.qgis.mapTools.createRelationship import CreateRelationship

class CreateRelationshipMapToolSingleton:

    tool = None

    @staticmethod
    def getInstance():
        if not CreateRelationshipMapToolSingleton.tool:
            CreateRelationshipMapToolSingleton.tool = CreateRelationship()
        return CreateRelationshipMapToolSingleton.tool