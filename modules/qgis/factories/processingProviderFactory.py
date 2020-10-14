from route_mapping.modules.qgis.factories.fpProcessingProviderSingleton import FPProcessingProviderSingleton

class ProcessingProviderFactory:

    def createProvider(self, typeName):
        typeNames = {
            'fp': FPProcessingProviderSingleton
        }
        return typeNames[typeName].getInstance()