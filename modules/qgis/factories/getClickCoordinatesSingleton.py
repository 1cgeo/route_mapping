
from route_mapping.modules.qgis.mapTools.getClickCoordinates import GetClickCoordinates

class GetClickCoordinatesSingleton:

    tool = None

    @staticmethod
    def getInstance():
        if not GetClickCoordinatesSingleton.tool:
            GetClickCoordinatesSingleton.tool = GetClickCoordinates()
        return GetClickCoordinatesSingleton.tool