from route_mapping.modules.qgis.inputs.rasterRemote import RasterRemote
from route_mapping.modules.qgis.inputs.rasterLocal import RasterLocal
from route_mapping.modules.qgis.inputs.postgis import Postgis
from route_mapping.modules.qgis.inputs.message import Message
from route_mapping.modules.qgis.inputs.browserUrl import BrowserUrl
from route_mapping.modules.qgis.inputs.wms import Wms
from route_mapping.modules.qgis.inputs.wfs import Wfs
from route_mapping.modules.qgis.inputs.virtualLayer import VirtualLayer

class InputDataFactory:

    def createInputDataType(self, typeNumber):
        types = {
            1: RasterLocal,
            2: RasterRemote,
            3: Postgis,
            4: Message,
            5: BrowserUrl,
            6: Wms,
            7: Wfs,
            8: Wms,
            100: VirtualLayer
        }
        if not(typeNumber in types):
            return
        return types[typeNumber]()