import os
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from route_mapping.widgets.widget import Widget

class RouteGeneratorDock(QtWidgets.QDockWidget, Widget):

    def __init__(self, mediator=None):
        super(RouteGeneratorDock, self).__init__()
        uic.loadUi(self.getUiPath(), self)
        self.mediator = mediator
        self.loadButtonSettings()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'routeGenerator.ui'
        )

    def closeEvent(self, e):
        self.getMediator().cleanGeneratorDockSettings()
        
    def loadButtonSettings(self):
        for setting in self.getButtonSettings():
            self.setButtonSettings(
                setting['button'],
                setting['pathIcon'],
                setting['toolTip']
            )

    def getButtonSettings(self):
        return [
            {
                'button': self.sourceCoordBtn,
                'pathIcon': os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    '..',
                    'icons',
                    'sourcePoint.svg'
                ),
                'toolTip': 'Obter ponto do mapa'
            },
            {
                'button': self.targetCoordBtn,
                'pathIcon': os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    '..',
                    'icons',
                    'targetPoint.svg'
                ),
                'toolTip': 'Obter ponto do mapa'
            },
            {
                'button': self.configBtn,
                'pathIcon': os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    '..',
                    'icons',
                    'config.png'
                ),
                'toolTip': 'Obter ponto do mapa'
            }
        ]

    def setButtonSettings(self, button, pathIcon, toolTip):
        button.setIcon(QtGui.QIcon(pathIcon))
        button.setIconSize(QtCore.QSize(24,24))
        button.setToolTip(toolTip)

    def getMediator(self):
        return self.mediator

    @QtCore.pyqtSlot(bool)
    def on_configBtn_clicked(self):
        self.getMediator().showConfigDialog()

    @QtCore.pyqtSlot(bool)
    def on_sourceCoordBtn_clicked(self):
        self.getMediator().activeCaptureSourceCoordinates(
            lambda x,y: self.sourceCoordLe.setText('{x};{y}'.format(x=x, y=y))
        )
    
    @QtCore.pyqtSlot(bool)
    def on_targetCoordBtn_clicked(self):
        self.getMediator().activeCaptureTargetCoordinates(
            lambda x,y: self.targetCoordLe.setText('{x};{y}'.format(x=x, y=y))
        )

    def isValidInput(self):
        return (
            len(self.sourceCoordLe.text().split(';')) == 2
            and
            len(self.targetCoordLe.text().split(';')) == 2
        )

    @QtCore.pyqtSlot(bool)
    def on_runBtn_clicked(self):
        if not self.isValidInput():
            self.showErrorMessageBox('Erro', 'Preencha todos os campos!')
            return
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            self.getMediator().buildRoute({
                'source': {
                    'x': self.sourceCoordLe.text().split(';')[0],
                    'y': self.sourceCoordLe.text().split(';')[1]
                },
                'target': {
                    'x': self.targetCoordLe.text().split(';')[0],
                    'y': self.targetCoordLe.text().split(';')[1]
                }
            })
        except:
            self.showErrorMessageBox('Erro', 'Rota não encontrada!')
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()


    def setRouteInfo(self, distance, time):
        self.routeInfoLb.setText('''
            <p><b>Distância total:</b> {km}{m}</p>
            <p><b>Tempo total:</b> {hours}{minutes}{seconds}</p>
            '''.format(
                km='{0} km'.format(distance[0]) if distance[0] else '',
                m=' {0} m'.format(distance[1]) if distance[1] else '',
                hours='{0} h'.format(time[0]) if time[0] else '',
                minutes=' {0} m'.format(time[1]) if time[1] else '',
                seconds=' {0} s'.format(time[2]) if time[2] else ''
            )
        )
    
    def addRouteStepInfo(self, name, distance, time):
        stepLb = QtWidgets.QLabel()
        stepLb.setText('''
            <p><b>Nome:</b> {name}</p>
            <p><b>Distância:</b> {km}{m}</p>
            <p><b>Tempo:</b> {hours}{minutes}{seconds}</p>
            '''.format(
                name=name if name else '',
                km='{0} km'.format(distance[0]) if distance[0] else '',
                m=' {0} m'.format(distance[1]) if distance[1] else '',
                hours='{0} h'.format(time[0]) if time[0] else '',
                minutes=' {0} m'.format(time[1]) if time[1] else '',
                seconds=' {0} s'.format(time[2]) if time[2] else ''
            )
        )
        stepLb.setStyleSheet("border-bottom-width: 1px; border-bottom-style: solid; border-radius: 0px;")
        self.stepsScrollWidget.layout().addWidget(stepLb)

    def removeAllRouteSteps(self):
        layout = self.stepsScrollWidget.layout()
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is None:
                continue
            widget.deleteLater()
            