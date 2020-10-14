from route_mapping.modules.utils.factories.messageFactory  import MessageFactory
from route_mapping.modules.utils.factories.cursorFactory  import CursorFactory

class UtilsFactory:

    def createMessageFactory(self):
        return MessageFactory()

    def createCursorFactory(self):
        return CursorFactory()