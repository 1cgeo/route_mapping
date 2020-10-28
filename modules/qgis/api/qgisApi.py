from route_mapping.modules.qgis.interfaces.IQgisApi import IQgisApi
from route_mapping.modules.qgis.factories.mapFunctionsFactory import MapFunctionsFactory
from route_mapping.modules.qgis.factories.mapToolsFactory import MapToolsFactory

from qgis.PyQt.QtXml import QDomDocument
from PyQt5 import QtCore, QtWidgets, QtGui 
from qgis import gui, core
import base64, os, processing
from qgis.utils import plugins, iface
from configparser import ConfigParser
from PyQt5.QtWidgets import QAction, QMenu
from PyQt5.QtGui import QIcon
import math

class QgisApi(IQgisApi):

    def __init__(self,
            mapFunctionsFactory=MapFunctionsFactory(),
            mapToolsFactory=MapToolsFactory()
        ):
       self.mapFunctionsFactory = mapFunctionsFactory
       self.mapToolsFactory = mapToolsFactory

    def setProjectVariable(self, key, value):
        chiper_text = base64.b64encode(value.encode('utf-8'))
        core.QgsExpressionContextUtils.setProjectVariable(
            core.QgsProject().instance(), 
            key,
            chiper_text.decode('utf-8')
        )

    def getProjectVariable(self, key):
        current_project  = core.QgsProject().instance()
        chiper_text = core.QgsExpressionContextUtils.projectScope(current_project).variable(
            key
        )
        value = base64.b64decode(str.encode(chiper_text)).decode('utf-8') if chiper_text else ''
        return value

    def setSettingsVariable(self, key, value):
        qsettings = QtCore.QSettings()
        qsettings.setValue(key, value)

    def getSettingsVariable(self, key):
        qsettings = QtCore.QSettings()
        return qsettings.value(key)


    def getShortcutKey(self, shortcutKeyName):
        keys = {
            'Y': QtCore.Qt.Key_Y,
            'B': QtCore.Qt.Key_B,
        }
        if not shortcutKeyName in keys:
            return
        return keys[shortcutKeyName]

    def createAction(self, name, iconPath, callback, shortcutKeyName, checkable):
        a = QAction(
            QIcon(iconPath),
            name,
            iface.mainWindow()
        )
        if self.getShortcutKey(shortcutKeyName):
            a.setShortcut(self.getShortcutKey(shortcutKeyName))
        a.setCheckable(checkable)
        a.triggered.connect(callback)
        return a

    def addActionDigitizeToolBar(self, action):
        iface.digitizeToolBar().addAction(action)

    def removeActionDigitizeToolBar(self, action):
        iface.digitizeToolBar().removeAction(action)

    def addDockWidget(self, dockWidget, side):
        if side == 'right':
            iface.addDockWidget(QtCore.Qt.RightDockWidgetArea, dockWidget)
        iface.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dockWidget)

    def removeDockWidget(self, dockWidget):
        if not dockWidget.isVisible():
            return
        iface.removeDockWidget(dockWidget)

    def getMapFunction(self, functionName):
        return self.mapFunctionsFactory.getFunction(functionName)

    def activeTool(self, toolName, unsetTool=False, settings=None):
        tool = self.mapToolsFactory.getTool(toolName)
        if unsetTool:
            self.unsetMapTool(tool)
            return
        if settings:
            tool.setSettings(settings)
        self.setMapTool(tool)
        return tool

    def setMapTool(self, tool):
        iface.mapCanvas().setMapTool(tool)

    def unsetMapTool(self, tool):
        iface.mapCanvas().unsetMapTool(tool)

    def addToolBar(self, name):
        return iface.addToolBar(name)

    def zoomToWkt(self, wkt):
        geom = core.QgsGeometry.fromWkt(wkt)
        iface.mapCanvas().setExtent(geom.boundingBox())
        iface.mapCanvas().refresh()
