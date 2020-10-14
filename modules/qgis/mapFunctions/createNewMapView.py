"""
/***************************************************************************
 newMapView
                                 A QGIS plugin
 Abre um novo "Map View" com as camadas selecionadas.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2020-03-18
        git sha              : $Format:%H$
        copyright            : (C) 2020 by Cardoso
        email                : cardoso.lara@eb.mil.br
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/"""

from qgis.utils import iface
from qgis import gui, core
from PyQt5 import QtWidgets
import math
from route_mapping.modules.qgis.mapFunctions.mapFunction import MapFunction

class CreateNewMapView(MapFunction):

    def __init__(self):
        super(CreateNewMapView, self).__init__()
    
    def createTheme(self):
        layers = iface.layerTreeView().selectedLayers()
        themeRecords = core.QgsMapThemeCollection.MapThemeRecord()
        [ themeRecords.addLayerRecord( core.QgsMapThemeCollection.MapThemeLayerRecord(layer) ) for layer in layers ]
        themeCollection = core.QgsProject.instance().mapThemeCollection()
        themeName = "{0}{1}".format(
            layers[0].name() if len(layers) == 1 else 'tema_misto',
            '' if len(themeCollection.mapThemes()) == 0 else len(themeCollection.mapThemes())
        )
        themeCollection.insert(themeName, themeRecords)
        return themeName

    def openMapView(self):
        for i in range(len(iface.viewMenu().actions())):
            if iface.viewMenu().actions()[i].objectName() == 'mActionNewMapCanvas':
                iface.viewMenu().actions()[i].trigger()
                return True
        return False

    def triggerTheme(self, ThemeName, mapView):
        qtoolBtn = mapView.findChildren(QtWidgets.QToolButton)[4]
        qtoolBtn.showMenu()
        menuThemes = qtoolBtn.menu()
        themesActions = menuThemes.actions()
        [ ta.trigger() for ta in themesActions if ta.text() == ThemeName]

    def getOpenMapView(self):
        docks = []
        for widget in iface.mainWindow().children():
            if not(type(widget) == QtWidgets.QDockWidget):
                continue
            if not(widget.objectName() == 'QgsMapCanvasDockWidgetBase'):
                continue
            docks.append(widget)
        return docks[-1]

    def settings(self, mapView, themeName):
        menuSettings = mapView.findChildren(QtWidgets.QToolButton)[5].menu()
        menuSettings.actions()[0].defaultWidget().children()[1].click()
        menuSettings.actions()[0].defaultWidget().children()[-3].setChecked(True)
        menuSettings.actions()[0].defaultWidget().children()[-1].setValue(1)
        self.triggerTheme(themeName, mapView)

    def run(self):
        if not self.openMapView():
            return (False, 'Falha ao criar novo mapa')
        themeName = self.createTheme()
        mapView = self.getOpenMapView()
        self.settings(mapView, themeName)
