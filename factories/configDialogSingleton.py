from route_mapping.widgets.configDialog import ConfigDialog

class ConfigDialogSingleton:

    configDialog = None

    @staticmethod
    def getInstance(mediator):
        if not ConfigDialogSingleton.configDialog:
            ConfigDialogSingleton.configDialog = ConfigDialog(mediator)
        return ConfigDialogSingleton.configDialog