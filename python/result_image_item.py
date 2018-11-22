from PyQt5 import QtCore
from PyQt5 import QtWidgets
from ui_result_image_item import Ui_Form
from test_result import TestResultImage, TestResultClass
from bbox_image_dialog import BBoxImageDialog


class ResultImageItem(QtWidgets.QWidget, Ui_Form):

    def __init__(self, parent=None, result_image=None, required_classes=None):
        super(QtWidgets.QWidget, self).__init__()
        self.setupUi(self)
        self.set_result_image(result_image, required_classes)

        # Make connection
        self.btnShowImageWithBox.clicked.connect(self.slot_clicked_show_bbox)

    def set_result_image(self, result_image, required_classes):
        self._result_image = result_image
        self._required_classes = required_classes
        self._setup_ui_with_result()

    def set_index(self, index):
        self.labelIndex.setText('{}'.format(index))

    def _setup_ui_with_result(self):
        if self._result_image is None or self._required_classes is None:
            raise ValueError('ResultImageItem: There is no valid data')

        self.labelImage.setText(
            self._result_image.name + ' (' + self._result_image.group_name + ')')

        found, missed, extra = self._get_found_and_missed_classes_str()

        if len(found) > 0:
            self.labelFound.setText(found)
        if len(missed) > 0:
            self.labelMissing.setText(missed)
        if len(extra) > 0:
            self.labelExtra.setText(extra)

        # Set color by status of found/missing/wrong
        if len(extra) > 0:
            # Yellow
            self.labelExtra.setStyleSheet('background-color: #ffffb7')
        elif len(missed) == 0:
            # Green
            self.labelFound.setStyleSheet('background-color: #b7ffb7')
        else:
            # Red
            self.labelMissing.setStyleSheet('background-color: #ffb7b7')

    def _get_found_and_missed_classes_str(self):
        found = list()
        missed = list()

        found_classes = list()
        for result_class in self._result_image.classes:
            found_classes.append(result_class.name)

        for requried_class in self._required_classes:
            if requried_class in found_classes:
                found.append(requried_class)
            else:
                missed.append(requried_class)

        extra_classes = set(found_classes) - set(self._required_classes)
        extra_classes = list(extra_classes)

        found = str(found).replace('\'', '').replace('[', '').replace(']', '')
        missed = str(missed).replace(
            '\'', '').replace('[', '').replace(']', '')
        extra = str(extra_classes).replace('\'', '').replace(
            '[', '').replace(']', '').replace(' ',  '')

        return found, missed, extra

    @QtCore.pyqtSlot()
    def slot_clicked_show_bbox(self):
        bbox_image_dialog = BBoxImageDialog(
            parent=self,
            filepath=self._result_image.filepath,
            result_classes=self._result_image.classes)
        bbox_image_dialog.exec_()
