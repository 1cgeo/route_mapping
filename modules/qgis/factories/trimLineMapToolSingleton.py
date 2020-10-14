from route_mapping.modules.qgis.mapTools.trimLine import TrimLine

class TrimLineMapToolSingleton:

    tool = None

    @staticmethod
    def getInstance():
        if not TrimLineMapToolSingleton.tool:
            TrimLineMapToolSingleton.tool = TrimLine()
        return TrimLineMapToolSingleton.tool