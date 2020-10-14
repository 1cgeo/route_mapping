from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt

from route_mapping.modules.utils.interfaces.ICursor  import ICursor

class Cursor(ICursor):

    def getImagePath(self):
        raise NotImplementedError('Abstract Method')

    def getScale(self):
        raise NotImplementedError('Abstract Method')
    
    def getCursor(self):
        with open(self.getImagePath(), "rb") as image:
            f = image.read()
            b = bytearray(f)
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData( b, "PNG", Qt.AutoColor  )
        w, h = self.getScale()
        pixmap = pixmap.scaled(w, h)
        hotX, hotY = self.getHotSpot(pixmap)
        return QtGui.QCursor(pixmap, hotX, hotY)