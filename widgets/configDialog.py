import os
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from route_mapping.widgets.widget import Widget
from route_mapping.modules.utils.decorators import cursorwait

class ConfigDialog(QtWidgets.QDialog, Widget):

    def __init__(self, mediator=None):
        super(ConfigDialog, self).__init__()
        uic.loadUi(self.getUiPath(), self)
        self.mediator = mediator
        self.mapConfig = {
            'dbUser': self.dbUserLe,
            'dbName': self.dbNameLe,
            'dbHost': self.dbHostLe,
            'dbPort': self.dbPortLe,
            'dbPass': self.dbPassLe
        }

    def showUp(self):
        self.show()
        self.activateWindow()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'configDialog.ui'
        )

    def getMediator(self):
        return self.mediator

    def load(self, data):
        for key in data:
            if not (key in self.mapConfig):
                continue
            self.mapConfig[key].setText(data[key])

    def dump(self):
        data = {}
        for key in self.mapConfig:
            data[key] = self.mapConfig[key].text()
        return data

    def isValidInput(self):
        for key in self.mapConfig:
            if not self.mapConfig[key].text():
                return False
        return True
        
    @QtCore.pyqtSlot(bool)
    def on_cancelBtn_clicked(self):
        self.close()

    @QtCore.pyqtSlot()
    @cursorwait
    def on_saveBtn_clicked(self):
        if self.isValidInput():
            self.getMediator().setRouteSettings(self.dump())
            self.accept()
            return
        self.showErrorMessageBox('Erro', 'Preencha todos os campos!')

    @QtCore.pyqtSlot()
    @cursorwait
    def on_saveAndLoadLayersBtn_clicked(self):
        if self.isValidInput():
            self.getMediator().setRouteSettings(self.dump())
            self.getMediator().loadRouteLayers()
            self.accept()
            return
        self.showErrorMessageBox('Erro', 'Preencha todos os campos!')