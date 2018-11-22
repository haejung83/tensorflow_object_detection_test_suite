import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtMultimedia
from PyQt5 import QtCore
from PyQt5 import uic 
from PyQt5.QtCore import pyqtSlot

from ui_mainwindow import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(QtWidgets.QMainWindow, self).__init__()
        self.setupUi(self)
