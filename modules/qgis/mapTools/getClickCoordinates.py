from qgis.core import QgsFeature
from qgis.gui import QgsMapToolIdentify
from PyQt5.QtCore import Qt, QPoint
from PyQt5 import QtWidgets, QtGui
from qgis.utils import iface
from qgis import gui, core
import os

from route_mapping.modules.qgis.mapTools.mapTool import MapTool

class  GetClickCoordinates(QgsMapToolIdentify, MapTool):
    
    def __init__(self):
        super(GetClickCoordinates, self).__init__(iface.mapCanvas())
        self.setCursor(Qt.CrossCursor)
        self.rubberBand = None

    def isValidSettings(self):
        return (
            ('callback' in self.getSettings() and self.getSettings()['callback'])
            and
            ('svgIconPath' in self.getSettings() and self.getSettings()['svgIconPath'])

        )

    def activate(self):
        super().activate()
        if self.isValidSettings():
            self.resetRubberBand()
            return
        self.showErrorMessageBox(
            iface.mainWindow(),
            'Erro',
            'Configurações inválidas. Para usar essa ferramento é necessário definir suas configurações.'
        )
        iface.mapCanvas().unsetMapTool(self)

    def canvasReleaseEvent(self, event):
        self.execute(event.mapPoint())

    def deactivate(self):
        super().deactivate()

    def resetRubberBand(self):
        if self.rubberBand:
            self.rubberBand.reset()
        self.rubberBand = gui.QgsRubberBand(
            iface.mapCanvas(), 
            geometryType = core.QgsWkbTypes.PointGeometry
        )
        self.rubberBand.setSvgIcon(self.getSettings()['svgIconPath'], QPoint(-12.5, -48))
        iface.mapCanvas().refresh()

    def execute(self, qgsPoint):
        self.getSettings()['callback'](qgsPoint.x(), qgsPoint.y())
        self.resetRubberBand()
        self.rubberBand.addPoint(qgsPoint)
        iface.mapCanvas().refresh()
        