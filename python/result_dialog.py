
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from ui_result_dialog import Ui_Dialog
from result_image_item import ResultImageItem


class ResultDialog(QtWidgets.QDialog, Ui_Dialog):
    _test_result = None

    def __init__(self, parent=None):
        super(QtWidgets.QDialog, self).__init__()
        self.setupUi(self)

    def set_test_result(self, test_result):
        self._test_result = test_result
        self._build_table_by_result()

    def _build_table_by_result(self):
        self.labelTestedCount.setText(str(self._test_result.tested_count))
        self.labelPassedCount.setText(str(self._test_result.passed_count))

        mark_group = True
        color_group = QtGui.QColor(0, 0, 0, alpha=20)

        result_image_index = 0
        for result_group in self._test_result.group:
            #set_of_required_classes = set(result_group.required_classes)
            for result_image in result_group.images:
                result_image.group_name = result_group.name
                result_image_item = ResultImageItem(
                    result_image=result_image, required_classes=result_group.required_classes)

                result_image_index = result_image_index + 1
                result_image_item.set_index(result_image_index)

                list_widget_item = QtWidgets.QListWidgetItem(
                    self.widgetResultList)
                list_widget_item.setSizeHint(result_image_item.sizeHint())

                if mark_group:
                    list_widget_item.setBackground(color_group)

                self.widgetResultList.addItem(list_widget_item)
                self.widgetResultList.setItemWidget(
                    list_widget_item, result_image_item)

            mark_group = not mark_group
