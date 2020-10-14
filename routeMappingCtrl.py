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
            guiFactory=GuiFactory()
        ):
        self.qgis = qgis
        self.messageFactory = messageFactory
        self.guiFactory = guiFactory
        self.actions = []
        self.routeGeneratorDock = None
        self.captureSourceCoordTool = None
        self.captureTargetCoordTool = None
        self.routeGeneratorDock = self.guiFactory.getWidget('RouteGeneratorDock', mediator=self)

    def loadPlugin(self):
        for actionSettings in self.getActionSettings():
            action = self.qgis.createAction(
                actionSettings['name'],
                actionSettings['iconPath'],
                actionSettings['callback']
            )
            self.qgis.addActionDigitizeToolBar(action)
            self.actions.append(action)

    def getActionSettings(self):
        return [
            {
                'name': 'Gerador de rotas',
                'iconPath':os.path.join(self.ROOT_PATH_ICON, 'route.png'),
                'callback': self.showRouteGeneratorDock
            },
            {
                'name': 'Restrição de rota',
                'iconPath':os.path.join(self.ROOT_PATH_ICON, 'turnRestriction.png'),
                'callback': self.activeCreateRelationshipTool
            }
        ]

    def unloadPlugin(self):
        self.qgis.activeTool('CreateRelationship', unsetTool=True)
        self.cleanGeneratorDockSettings()
        [self.qgis.removeActionDigitizeToolBar(action) for action in self.actions ]

    def activeCreateRelationshipTool(self):
        settings = {
            'maxSelection': 2,
            'layer': {
                    'name': 'rot_trecho_rede_rodoviaria_l',
                    'fieldName': 'id'
            }, 
            'relationship': {
                'name': 'rot_restricao',
                'fieds': [ 'id_1', 'id_2']
            }
        }
        self.qgis.activeTool('CreateRelationship', settings=settings)

    def showRouteGeneratorDock(self):
        self.qgis.addDockWidget(self.routeGeneratorDock, side='left') 

    def cleanGeneratorDockSettings(self):
        self.captureSourceCoordTool.resetRubberBand()
        self.captureTargetCoordTool.resetRubberBand()

    def activeCaptureSourceCoordinates(self, setCoordinate):
        if self.captureSourceCoordTool:
            self.qgis.setMapTool(self.captureSourceCoordTool)
            return
        settings = {
            'callback': setCoordinate,
            'svgIconPath': os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'icons',
                'sourcePoint.svg'
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
                'targetPoint.svg'
            )
        }
        self.captureTargetCoordTool = self.qgis.activeTool('GetClickCoordinates', settings=settings)

    def showInfoMessageBox(self, parent, title, message):
        messageDlg = self.messageFactory.createMessage('InfoMessageBox')
        messageDlg.show(parent, title, message)
    
    def showErrorMessageBox(self, parent, title, message):
        messageDlg = self.messageFactory.createMessage('ErrorMessageBox')
        messageDlg.show(parent, title, message)

    def buildRoute(self, points):
        buildRoute = self.qgis.getMapFunction('BuildRoute')
        routeSettings = self.getRouteSettings()
        if not routeSettings:
            self.showErrorMessageBox(
                self.qgis.getMainWindow(),
                'Erro',
                'Preencha as configurações!'
            )
            return
        buildRoute.run(points, routeSettings)

    def getRouteSettings(self):
        routeSettings = self.qgis.getSettingsVariable('routeSettings')
        return json.loads(routeSettings) if routeSettings else {}
        
    def showConfigDialog(self):
        configDialog = self.guiFactory.getWidget('ConfigDialog', mediator=self)
        routeSettings = self.getRouteSettings()
        configDialog.load(routeSettings) if routeSettings else ''
        if not configDialog.exec_():
            return
        self.qgis.setSettingsVariable('routeSettings', json.dumps(configDialog.dump()))
        