from route_mapping.modules.qgis.factories.mapFunctionsFactory import MapFunctionsFactory
from route_mapping.modules.utils.factories.utilsFactory import UtilsFactory
from qgis.utils import iface
from qgis import gui, core

class MapTool:
    
    def __init__(self,
            mapFunctionsFactory=MapFunctionsFactory(),
            messageFactory=UtilsFactory().createMessageFactory(),
            cursorFactory=UtilsFactory().createCursorFactory()        
        ):
        super(MapTool, self).__init__()
        self.mapFunctionsFactory = mapFunctionsFactory
        self.messageFactory = messageFactory
        self.cursorFactory = cursorFactory
        self.settings = None

    def getCursor(self, cursorType):
        return self.cursorFactory.getCursor(cursorType)

    def setSettings(self, settings):
        self.settings = settings

    def getSettings(self):
        return self.settings

    def removeAllSelection(self):
        for a in iface.attributesToolBar().actions(): 
            if a.objectName() == 'mActionDeselectAll':
                a.trigger()
                break

    def showErrorMessageBox(self, parent, title, message):
        messageDlg = self.messageFactory.createMessage('ErrorMessageBox')
        messageDlg.show(parent, title, message)
