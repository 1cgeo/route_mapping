from route_mapping.modules.utils.message.htmlMessageDialog  import HtmlMessageDialog
from route_mapping.modules.utils.message.infoMessageBox  import InfoMessageBox
from route_mapping.modules.utils.message.errorMessageBox  import ErrorMessageBox
from route_mapping.modules.utils.message.questionMessageBox  import QuestionMessageBox

class MessageFactory:

    def createMessage(self, messageType):
        messageTypes = {
            'HtmlMessageDialog': HtmlMessageDialog,
            'InfoMessageBox': InfoMessageBox,
            'ErrorMessageBox': ErrorMessageBox,
            'QuestionMessageBox': QuestionMessageBox

        }
        return messageTypes[messageType]()