from PyQt5 import QtWidgets, QtGui, QtCore, uic

from route_mapping.modules.utils.factories.utilsFactory  import UtilsFactory

class Widget(QtCore.QObject):

    def __init__(self,
            messageFactory=UtilsFactory().createMessageFactory()
        ):
        super(Widget, self).__init__()
        self.messageFactory = messageFactory

    def showInfoMessageBox(self, title, message):
        messageDlg = self.messageFactory.createMessage('InfoMessageBox')
        messageDlg.show(self, title, message)
    
    def showErrorMessageBox(self, title, message):
        messageDlg = self.messageFactory.createMessage('ErrorMessageBox')
        messageDlg.show(self, title, message)