from route_mapping.widgets.routeGeneratorDock import RouteGeneratorDock
from route_mapping.factories.configDialogSingleton import ConfigDialogSingleton

class GuiFactory:

    def getWidget(self, widgetName, mediator):
        widgets = {
            'RouteGeneratorDock' : RouteGeneratorDock,
            'ConfigDialog': self.createConfigDialog,
        }
        return widgets[widgetName](mediator)

    def createConfigDialog(self, mediator):
        return ConfigDialogSingleton.getInstance(mediator)