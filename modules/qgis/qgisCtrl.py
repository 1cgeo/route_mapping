from route_mapping.modules.qgis.interfaces.IQgisCtrl import IQgisCtrl
from route_mapping.modules.qgis.factories.qgisApiSingleton import QgisApiSingleton
from qgis.utils import iface


class QgisCtrl(IQgisCtrl):

    def __init__(
            self,
            apiQGis=QgisApiSingleton.getInstance()
        ):
        super(QgisCtrl, self).__init__()
        self.iface = iface
        self.apiQGis = apiQGis

    def getMainWindow(self):
        return self.iface.mainWindow()

    def setProjectVariable(self, key, value):
        self.apiQGis.setProjectVariable(key, value)

    def getProjectVariable(self, key):
        return self.apiQGis.getProjectVariable(key)

    def setSettingsVariable(self, key, value):
        self.apiQGis.setSettingsVariable(key, value)

    def getSettingsVariable(self, key):
        return self.apiQGis.getSettingsVariable(key)

    def addDockWidget(self, dockWidget, side='right'):
        self.apiQGis.addDockWidget(dockWidget, side)

    def removeDockWidget(self, dockWidget):
        self.apiQGis.removeDockWidget(dockWidget)

    def addActionDigitizeToolBar(self, action):
        self.apiQGis.addActionDigitizeToolBar(action)

    def removeActionDigitizeToolBar(self, action):
        self.apiQGis.removeActionDigitizeToolBar(action)
    
    def createAction(self, name, iconPath, callback, shortcutKeyName='', checkable=False):
        return self.apiQGis.createAction(name, iconPath, callback, shortcutKeyName, checkable)

    def deleteAction(self, action):
        self.apiQGis.deleteAction(action)

    def activeTool(self, toolName, unsetTool=False, settings=None):
        return self.apiQGis.activeTool(toolName, unsetTool, settings)

    def setMapTool(self, tool):
        self.apiQGis.setMapTool(tool)

    def unsetMapTool(self, tool):
        self.apiQGis.unsetMapTool(tool)

    def getMapFunction(self, functionName):
        return self.apiQGis.getMapFunction(functionName)