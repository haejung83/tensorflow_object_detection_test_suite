import numpy as np

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

OFFSET_HEIGHT_LABEL_AND_BOX = 3.
OFFSET_HEIGHT_LABEL_ON_TOP = 14
OFFSET_WIDTH_LABEL_ON_TOP = 2

RESERVED_COLOR_TABLE = [
    QtCore.Qt.yellow,
    QtCore.Qt.red,
    QtCore.Qt.blue,
    QtCore.Qt.magenta,
    QtCore.Qt.cyan,
    QtCore.Qt.green,
]

class BBoxImageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image = QtGui.QImage()

    def set_image_with_filepath(self, filepath):
        self._image = QtGui.QImage(filepath)
        self.update()

    def set_result_classes(self, result_classes):
        self._result_classes = result_classes
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        if self._image is not None:
            self._image = self._image.scaled(self.size())
        
            painter.drawImage(0, 0, self._image)

            image_width = self._image.width()
            image_height = self._image.height()

            for index, result_class in enumerate(self._result_classes):
                color_index = index % len(RESERVED_COLOR_TABLE)
                current_color = RESERVED_COLOR_TABLE[color_index]
                box = result_class.box
                # Calculate coordinate
                target_x = box[1]*image_width
                target_y = box[0]*image_height
                target_width = (box[3]*image_width) - target_x
                target_height = (box[2]*image_height) - target_y
                # Change color
                painter.setPen(current_color)
                # Draw Rectangle
                painter.drawRect(target_x, target_y, target_width, target_height)
                # Draw class name with score on top of rectangle
                painter.drawText(QtCore.QPoint(target_x, target_y - OFFSET_HEIGHT_LABEL_AND_BOX), '{} ({:03.1f}%)'.format(result_class.name, (result_class.score*100.0)))
                # Draw class name with score on top of image for navigation
                painter.drawText(QtCore.QPoint(OFFSET_WIDTH_LABEL_ON_TOP, OFFSET_HEIGHT_LABEL_ON_TOP * (index+1)), '{} ({:03.1f}%)'.format(result_class.name, (result_class.score*100.0)))

