from qgis.utils import iface
from qgis import gui, core
import math
from route_mapping.modules.qgis.mapFunctions.mapFunction import MapFunction

class CreateRelationship(MapFunction):

    def __init__(self):
        super(CreateRelationship, self).__init__()

    def hasRelationship(self, attributes, layer):
        fi = layer.getFeatures()
        f = core.QgsFeature()
        while fi.nextFeature(f):
            if all([ f[name] == attributes[name] for name in attributes ]):
                return f
    
    def addRelationship(self, attributes, layer):
        relationshipFeature = core.QgsFeature()
        relationshipFeature.setFields(layer.fields())
        for name in attributes:
            relationshipFeature[name] = attributes[name]
        layer.startEditing()
        layer.addFeature(relationshipFeature)
        layer.commitChanges()

    def delRelationship(self, feature, layer):
        layer.startEditing()
        layer.deleteFeature(feature[0])
        layer.commitChanges()

    def run(self, attributes, relationshipTablaName):
        foundRelationshipTable = [
            layer
            for layer in core.QgsProject().instance().mapLayers().values()
            if layer.dataProvider().uri().table() == relationshipTablaName
        ]
        if not foundRelationshipTable:
            return (False, 'Tabela de relacionamento não encontrada')
        layer = foundRelationshipTable[0]

        feature = self.hasRelationship(attributes, layer)
        if feature:
            self.delRelationship(feature, layer)
        else:
            self.addRelationship(attributes, layer)
        iface.mapCanvas().refresh()
        return (True, '')
