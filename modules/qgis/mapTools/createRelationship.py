from qgis.core import QgsFeature
from qgis.gui import QgsMapToolIdentify
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets, QtGui
from qgis.utils import iface
from qgis import gui, core
import os

from route_mapping.modules.qgis.mapTools.mapTool import MapTool

class  CreateRelationship(QgsMapToolIdentify, MapTool):
    
    def __init__(self):
        super(CreateRelationship, self).__init__(iface.mapCanvas())
        self.setCursor(Qt.CrossCursor)
        self.selectedFeatureIds = []

    def isValidSettings(self):
        return self.getSettings() and len(self.getSettings()) > 0

    def activate(self):
        super().activate()
        if self.isValidSettings():
            iface.mapCanvas().setCursor(self.getCursor('Tap'))
            return
        self.showErrorMessageBox(
            iface.mainWindow(),
            'Erro',
            'Configurações inválidas. Para usar essa ferramento é necessário definir suas configurações.'
        )
        iface.mapCanvas().unsetMapTool(self)

    def getLayerNameToSelect(self):
        return self.getSettings()['layer']['name']

    def getForeignKeyLayer(self, layer):
        return self.getSettings()['layer']['fieldName']

    def getMaxSelection(self):
        return self.getSettings()['maxSelection']

    def getRelationshipTableName(self):
        return self.getSettings()['relationship']['name']

    def getRelationshipFieldNames(self):
        return self.getSettings()['relationship']['fieds']

    def canvasReleaseEvent(self, event):
        foundFeatures = self.identify(event.x(), event.y(), self.ActiveLayer, self.VectorLayer)
        if not foundFeatures:
            self.cleanSelections()
            return
        validFeatures = [
            feat
            for feat in foundFeatures
            if (
                feat.mLayer.type() == core.QgsMapLayer.VectorLayer
                and
                feat.mLayer.dataProvider().uri().table() in self.getLayerNameToSelect()
            )
        ]
        if not validFeatures:
            return
        feature = validFeatures[0].mFeature
        layer = validFeatures[0].mLayer
        fkValue = feature[self.getForeignKeyLayer()]
        if fkValue in self.selectedFeatureIds:
            self.selectedFeatureIds.remove(fkValue)        
            return
        self.selectedFeatureIds.append(fkValue)
        if not(len(self.selectedFeatureIds) == self.getMaxSelection()):
            return
        self.execute()
        self.cleanSelections()

    def cleanSelections(self):
        self.selectedFeatureIds = []

    def execute(self):
        QtWidgets.QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            attributes = dict(zip(self.getRelationshipFieldNames(), self.selectedFeatureIds))
            createRelationship = self.mapFunctionsFactory.getFunction('CreateRelationship')
            result = createRelationship.run(attributes, self.getRelationshipTableName())
            if not result[0]:
                self.showErrorMessageBox(
                    iface.mainWindow(),
                    'Erro',
                    result[1]
                )
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        