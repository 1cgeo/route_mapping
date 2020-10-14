from route_mapping.modules.qgis.processingAlgs.processingProvider import ProcessingProvider

class FPProcessingProviderSingleton:

    provider = None

    @staticmethod
    def getInstance():
        if not FPProcessingProviderSingleton.provider:
            FPProcessingProviderSingleton.provider = ProcessingProvider()
        return FPProcessingProviderSingleton.provider