import os
from PyQt5 import QtWidgets, QtGui, QtCore, uic
from route_mapping.widgets.widget import Widget
from route_mapping.modules.utils.decorators import cursorwait

class RouteGeneratorDock(QtWidgets.QDockWidget, Widget):

    def __init__(self, mediator=None):
        super(RouteGeneratorDock, self).__init__()
        uic.loadUi(self.getUiPath(), self)
        self.mediator = mediator
        self.loadButtonSettings()
        self.loadInputSettings()
        self.stepsListWidget.itemDoubleClicked.connect(self.zoomToStep)

    @cursorwait
    def zoomToStep(self, item):
        stepLb = self.stepsListWidget.itemWidget(item)
        self.getMediator().zoomToWkt(stepLb.geomWkt)

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'routeGeneratorDock.ui'
        )

    def closeEvent(self, e):
        self.reset()
        
    def loadInputSettings(self):
        doubleValidator =  QtGui.QDoubleValidator(0, 300, 6, self)
        self.widthLe.setValidator(doubleValidator)
        self.heightLe.setValidator(doubleValidator)
        self.tonnageLe.setValidator(doubleValidator)
        self.maximumSpeedLe.setValidator(doubleValidator)

    def loadButtonSettings(self):
        for setting in self.getButtonSettings():
            self.setButtonSettings(
                setting['button'],
                setting['iconPath'],
                setting['toolTip']
            )

    def getButtonSettings(self):
        return [
            {
                'button': self.sourceCoordBtn,
                'iconPath': os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    '..',
                    'icons',
                    'sourcePoint.svg'
                ),
                'toolTip': 'Obter ponto do mapa'
            },
            {
                'button': self.targetCoordBtn,
                'iconPath': os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    '..',
                    'icons',
                    'targetPoint.svg'
                ),
                'toolTip': 'Obter ponto do mapa'
            },
            {
                'button': self.changeCoordBtn,
                'iconPath': os.path.join(
                    os.path.abspath(os.path.dirname(__file__)),
                    '..',
                    'icons',
                    'change.svg'
                ),
                'toolTip': 'Inverter coordenadas'
            }
        ]

    def setButtonSettings(self, button, pathIcon, toolTip):
        button.setIcon(QtGui.QIcon(pathIcon))
        button.setIconSize(QtCore.QSize(24,24))
        button.setToolTip(toolTip)

    def getMediator(self):
        return self.mediator

    @QtCore.pyqtSlot(bool)
    def on_changeCoordBtn_clicked(self):
        targetPoint = self.sourceCoordLe.text().split(';')
        sourcePoint = self.targetCoordLe.text().split(';')
        if len(targetPoint) == 2:
            self.targetCoordLe.setText('{x};{y}'.format(x=targetPoint[0], y=targetPoint[1]))
            self.getMediator().setTargetCoordToolPoint(targetPoint)
        if len(sourcePoint) == 2:
            self.sourceCoordLe.setText('{x};{y}'.format(x=sourcePoint[0], y=sourcePoint[1]))
            self.getMediator().setSourceCoordToolPoint(sourcePoint)
            

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

    def reset(self):
        self.sourceCoordLe.setText('')
        self.targetCoordLe.setText('')
        self.widthLe.setText('')
        self.heightLe.setText('')
        self.tonnageLe.setText('')
        self.maximumSpeedLe.setText('')
        self.largeVehicleCbx.setChecked(False)
        self.routeInfoLb.setText('')
        self.removeAllRouteSteps()
        self.getMediator().cleanRouteMarkers()

    @QtCore.pyqtSlot(bool)
    def on_resetBtn_clicked(self):
        self.reset()

    def isValidInput(self):
        return (
            len(self.sourceCoordLe.text().split(';')) == 2
            and
            len(self.targetCoordLe.text().split(';')) == 2
        )

    @QtCore.pyqtSlot()
    @cursorwait
    def on_runBtn_clicked(self):
        if not self.isValidInput():
            self.showErrorMessageBox('Erro', 'Preencha as coordenadas de início e fim!')
            return
        try:
            self.getMediator().buildRoute(
                (self.sourceCoordLe.text().split(';')[0], self.sourceCoordLe.text().split(';')[1]),
                (self.targetCoordLe.text().split(';')[0], self.targetCoordLe.text().split(';')[1]),
                (
                self.widthLe.text().replace(',', '.'), 
                self.heightLe.text().replace(',', '.'), 
                self.tonnageLe.text().replace(',', '.'), 
                self.maximumSpeedLe.text().replace(',', '.'),
                    self.largeVehicleCbx.isChecked()
                )
            )
        except Exception as e:
            self.showErrorMessageBox(
                'Erro', 
                'Rota não encontrada!'
            )
            
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
    
    def addRouteStepInfo(self, 
            name, 
            distance, 
            time, 
            initials, 
            covering, 
            tracks, 
            velocity, 
            note,
            geomWkt
        ):
        stepLb = QtWidgets.QLabel()
        stepLb.geomWkt = geomWkt
        stepLb.setText('''
            {name}
            {initials}
            {covering}
            {tracks}
            {velocity}
            <p><b>Distância:</b> {km}{m}</p>
            <p><b>Tempo:</b> {hours}{minutes}{seconds}</p>
            {note}
            '''.format(
                name='<p><b>Nome:</b> {0}</p>'.format(name) if name else '',
                initials='<p><b>Nome:</b> {0}</p>'.format(initials) if initials else '',
                covering='<p><b>Revestimento:</b> {0}</p>'.format(covering) if covering else '',
                tracks='<p><b>Faixas:</b> {0}</p>'.format(tracks) if tracks else '',
                velocity='<p><b>Velocidade (km/h):</b> {0}</p>'.format(velocity) if velocity else '',
                km='{0} km'.format(distance[0]) if distance[0] else '',
                m=' {0} m'.format(distance[1]) if distance[1] else '',
                hours='{0} h'.format(time[0]) if time[0] else '',
                minutes=' {0} m'.format(time[1]) if time[1] else '',
                seconds=' {0} s'.format(time[2]) if time[2] else '',
                note='<p><b>Observações:</b> {0}</p>'.format(note) if note else '',
            )
        )
        stepLb.setStyleSheet("border-bottom-width: 1px; border-bottom-style: solid; border-radius: 0px;")
        #self.stepsScrollWidget.layout().addWidget(stepLb)
        itemN = QtWidgets.QListWidgetItem() 
        #Create widget
        itemN.setSizeHint(stepLb.sizeHint())    

        #Add widget to QListWidget funList
        self.stepsListWidget.addItem(itemN)
        self.stepsListWidget.setItemWidget(itemN, stepLb)

    def removeAllRouteSteps(self):
        self.stepsListWidget.clear()
            