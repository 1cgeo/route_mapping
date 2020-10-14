from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt
import os

from route_mapping.modules.utils.cursors.cursor  import Cursor

class Tap(Cursor):

    def __init__(self):
        super(Tap, self).__init__()

    def getImagePath(self):
        return os.path.join(
            os.path.abspath(os.path.join(
                os.path.dirname(__file__)
            )),
            'images',
            'tap.png'
        )

    def getScale(self):
        return (28, 28)

    def getHotSpot(self, pixmap):
        return pixmap.width()/2, 0