from route_mapping.config import Config
from route_mapping.factories.guiFactory import GuiFactory
import os, json

class RouteMappingCtrl:

    ROOT_PATH_ICON = os.path.join(
            os.path.dirname(__file__),
            'icons'
    )

    def __init__(self,
            qgis,
            messageFactory,
            guiFactory=GuiFactory(),
        ):
        self.qgis = qgis
        self.messageFactory = messageFactory
        self.guiFactory = guiFactory
        self.actions = []
        self.routeGeneratorDock = None
        self.captureSourceCoordTool = None
        self.captureTargetCoordTool = None
        self.pluginToolBar = None
        self.pluginToolBar = self.qgis.addToolBar("Ferramentas de Rotas")
        self.routeGeneratorDock = self.guiFactory.getWidget('RouteGeneratorDock', mediator=self)

    def getRouteGeneratorDock(self):
        return self.routeGeneratorDock

    def showInfoMessageBox(self, parent, title, message):
        messageDlg = self.messageFactory.createMessage('InfoMessageBox')
        messageDlg.show(parent, title, message)
    
    def showErrorMessageBox(self, parent, title, message):
        messageDlg = self.messageFactory.createMessage('ErrorMessageBox')
        messageDlg.show(parent, title, message)

    def showQuestionMessageBox(self, parent, title, message):
        messageDlg = self.messageFactory.createMessage('QuestionMessageBox')
        return messageDlg.show(parent, title, message)

    def loadPlugin(self):
        for actionSettings in self.getActionSettings():
            action = self.qgis.createAction(
                actionSettings['toolTip'],
                actionSettings['iconPath'],
                actionSettings['callback']
            )
            self.pluginToolBar.addAction(action)
            self.actions.append(action)

    def getActionSettings(self):
        return [
            {
                'toolTip': 'Gerador de rotas',
                'iconPath':os.path.join(self.ROOT_PATH_ICON, 'route.png'),
                'callback': self.showRouteGeneratorDock
            },
            {
                'toolTip': 'Restrição de rota',
                'iconPath':os.path.join(self.ROOT_PATH_ICON, 'turnRestriction.png'),
                'callback': self.activeCreateRelationshipTool
            },
            {
                'toolTip': 'Gerar rede de rotas',
                'iconPath':os.path.join(self.ROOT_PATH_ICON, 'transform.png'),
                'callback': self.createRouteNetwork
            },
            {
                'toolTip': 'Configurações',
                'iconPath':os.path.join(self.ROOT_PATH_ICON, 'config.png'),
                'callback': self.showConfigDialog
            }
        ]

    def unloadPlugin(self):
        self.qgis.activeTool('CreateRelationship', unsetTool=True)
        self.cleanGeneratorDockSettings()
        self.pluginToolBar.close()

    def activeCreateRelationshipTool(self):
        if not self.validateSettings():
            return
        routeSettings = self.getRouteSettings()
        settings = {
            'maxSelection': 2,
            'layer': {
                'schema': 'edgv',
                'name': 'rot_trecho_rede_rodoviaria_l',
                'fieldName': 'id'
            }, 
            'relationship': {
                'schema': 'edgv',
                'name': 'rot_restricao',
                'fieds': [ 'id_1', 'id_2']
            }
        }
        self.qgis.activeTool('CreateRelationship', settings=settings)

    def showRouteGeneratorDock(self):
        self.qgis.addDockWidget(self.routeGeneratorDock, side='left') 

    def cleanGeneratorDockSettings(self):
        self.captureSourceCoordTool.resetRubberBand() if self.captureSourceCoordTool else ''
        self.captureTargetCoordTool.resetRubberBand() if self.captureTargetCoordTool else ''
        self.routeGeneratorDock.close()

    def activeCaptureSourceCoordinates(self, setCoordinate):
        if self.captureSourceCoordTool:
            self.qgis.setMapTool(self.captureSourceCoordTool)
            return
        settings = {
            'callback': setCoordinate,
            'svgIconPath': os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'icons',
                'sourcePointMarker.svg'
            )
        }
        self.captureSourceCoordTool = self.qgis.activeTool('GetClickCoordinates', settings=settings)

    def activeCaptureTargetCoordinates(self, setCoordinate):
        if self.captureTargetCoordTool:
            self.qgis.setMapTool(self.captureTargetCoordTool)
            return
        settings = {
            'callback': setCoordinate,
            'svgIconPath': os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'icons',
                'targetPointMarker.svg'
            )
        }
        self.captureTargetCoordTool = self.qgis.activeTool('GetClickCoordinates', settings=settings)

    def buildRoute(self, 
            sourcePoint, 
            targetPoint, 
            vehicle
        ):
        if not self.validateSettings():
                return
        buildRoute = self.qgis.getMapFunction('BuildRoute')
        routeSettings = self.getRouteSettings()
        route = buildRoute.run(
            sourcePoint,
            targetPoint,
            'edgv',
            'rot_trecho_rede_rodoviaria_l',
            'edgv',
            'rot_restricao',
            (
                routeSettings['dbName'], 
                routeSettings['dbHost'], 
                routeSettings['dbPort'], 
                routeSettings['dbUser'], 
                routeSettings['dbPass']
            ),
            vehicle
        )
        self.showRouteInfo(route)


    def showRouteInfo(self, route):
        self.routeGeneratorDock.removeAllRouteSteps()
        getNumberDecimal = lambda n: float(str(n-int(n))[1:] if str(n-int(n))[1:] != '' else 0)
        def formatDistance(totalKm):
            km = int(totalKm)
            m = int(getNumberDecimal(totalKm)*1000)
            return (km, m)
        def formatTime(totalHours):
            hours = int(totalHours)
            minutes = int(getNumberDecimal(totalHours)*60) 
            seconds = int(getNumberDecimal(getNumberDecimal(totalHours)*60)*60)
            return (hours, minutes, seconds)
        totalKm = 0
        totalHours = 0
        for step in route:
            name = step['name']
            hours = step['hours'] if step['hours'] else 0
            time = formatTime(hours)
            km = step['distancekm'] if step['distancekm'] else 0
            distance = formatDistance(km)
            self.routeGeneratorDock.addRouteStepInfo(
                name, 
                distance, 
                time,
                step['initials'], 
                step['paving'], 
                step['tracks'], 
                step['velocity'], 
                step['note']
            )
            totalKm += km
            totalHours += hours
        distance = formatDistance(totalKm)
        time = formatTime(totalHours)
        self.routeGeneratorDock.setRouteInfo(distance, time)

    def validateSettings(self):
        if self.hasRouteSettings():
            return True
        self.showErrorMessageBox(
            self.qgis.getMainWindow(),
            'Erro',
            'Preencha as configurações!'
        )
        return False
        
    def hasRouteSettings(self):
        return self.getRouteSettings()

    def getRouteSettingsKey(self):
        return 'routeSettings:v2'

    def getRouteSettings(self):
        routeSettings = self.qgis.getSettingsVariable(self.getRouteSettingsKey())
        return json.loads(routeSettings) if routeSettings else {}

    def setRouteSettings(self, routeSettings):
        self.qgis.setSettingsVariable(self.getRouteSettingsKey(), json.dumps(routeSettings))
        
    def showConfigDialog(self):
        configDialog = self.guiFactory.getWidget('ConfigDialog', mediator=self)
        configDialog.load(self.getRouteSettings()) if self.hasRouteSettings() else ''
        configDialog.showUp()
        
    def createRouteNetwork(self, b):
        if not self.validateSettings():
            return
        if not self.showQuestionMessageBox(
                self.qgis.getMainWindow(),
                'Aviso',
                '''<p>Gerar uma rede de rotas?</p>
                  <p style="color:red">Atenção: caso já exista uma rede de rotas ela será deletada.</p>'''
            ):
            return
        buildRouteStructure = self.qgis.getMapFunction('BuildRouteStructure')
        routeSettings = self.getRouteSettings()
        success = buildRouteStructure.run(
            'edgv',
            'rot_trecho_rede_rodoviaria_l',
            routeSettings['dbName'], 
            routeSettings['dbHost'], 
            routeSettings['dbPort'], 
            routeSettings['dbUser'], 
            routeSettings['dbPass']
        )
        messageBox = self.showInfoMessageBox if success else self.showErrorMessageBox
        messageBox(
            self.qgis.getMainWindow(),
            'Aviso' if success else 'Erro',
            'Rede gerada com sucesso!' if success else 'Erro ao gerar rede!'
        )
        