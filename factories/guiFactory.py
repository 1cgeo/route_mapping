from route_mapping.widgets.routeGeneratorDock import RouteGeneratorDock
from route_mapping.widgets.configDialog import ConfigDialog

class GuiFactory:

    def getWidget(self, widgetName, mediator):
        widgets = {
            'RouteGeneratorDock' : RouteGeneratorDock,
            'ConfigDialog': ConfigDialog,
        }
        return widgets[widgetName](mediator)