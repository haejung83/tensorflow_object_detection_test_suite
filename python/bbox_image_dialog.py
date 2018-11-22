
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from ui_bbox_image_dialog import Ui_Dialog


class BBoxImageDialog(QtWidgets.QDialog, Ui_Dialog):

    def __init__(self, parent=None, filepath=None, result_classes=None):
        super(QtWidgets.QDialog, self).__init__(parent)
        self.setupUi(self)

        if filepath is not None:
            self.widget.set_image_with_filepath(filepath)

        if result_classes is not None:
            self.widget.set_result_classes(result_classes)

    def set_image_filepath(self, filepath):
        self.widget.set_image_with_filepath(filepath)

    def set_result_classes(self, result_classes):
        self.widget.set_result_classes(result_classes)
