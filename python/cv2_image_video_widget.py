import numpy as np

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui


class CV2ImageVideoWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image = QtGui.QImage()

    @QtCore.pyqtSlot(np.ndarray)
    def slot_cv2_image(self, image_nd_array):
        self._image = self.get_qimage(image_nd_array, self.size())
        self.update()

    def get_qimage(self, image: np.ndarray, size=None):
        height, width, _ = image.shape

        bytesPerLine = 3 * width
        qimage = QtGui.QImage(image.data,
                              width,
                              height,
                              bytesPerLine,
                              QtGui.QImage.Format_RGB888)

        qimage = qimage.scaled(size)

        return qimage.rgbSwapped()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        if self._image is not None:
            painter.drawImage(0, 0, self._image)
