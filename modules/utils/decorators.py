from functools import wraps
from PyQt5 import QtWidgets, QtGui, QtCore

def cursorwait(func):
    @wraps(func)
    def inner(*args, **kwargs):
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            return func(*args, **kwargs)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor() 
    return inner