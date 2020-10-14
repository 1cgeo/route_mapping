import os, sys
from qgis import core, gui
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon

from route_mapping.modules.utils.factories.utilsFactory import UtilsFactory
from route_mapping.modules.qgis.qgisCtrl import QgisCtrl
from route_mapping.routeMappingCtrl import RouteMappingCtrl

class Main(QObject):

    

    def __init__(self, iface):
        super(Main, self).__init__()
        self.plugin_dir = os.path.dirname(__file__)
        self.qgis = QgisCtrl()
        self.routeMappingCtrl = RouteMappingCtrl(
            qgis=self.qgis,
            messageFactory=UtilsFactory().createMessageFactory()
        )

    def initGui(self):
        self.routeMappingCtrl.loadPlugin()
        
    def unload(self):
        self.routeMappingCtrl.unloadPlugin()