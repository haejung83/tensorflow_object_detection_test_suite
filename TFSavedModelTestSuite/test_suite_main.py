import sys
from PyQt5 import QtWidgets
from mainwindow import MainWindow


# Start here
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())