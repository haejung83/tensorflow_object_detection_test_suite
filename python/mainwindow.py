from PyQt5 import QtWidgets
from PyQt5 import QtCore

from ui_mainwindow import Ui_MainWindow
from config import Config
from config import CONFIG_KEY_SAVED_MODEL_PATH
from config import CONFIG_KEY_LABEL_MAP_PATH
from config import CONFIG_KEY_TEST_DATA_PATH
from config import CONFIG_KEY_RESULT_CUTOFF_THRESHOLD
from test_worker import TestWorker
from test_result import TestResult, TestResultGroup, TestResultClass
from result_dialog import ResultDialog

import sys
import os
import time

_PATH_INDEX_SAVED_MODEL = 0
_PATH_INDEX_LABEL_MAP = 1
_PATH_INDEX_TEST_DATA = 2

_PATH_INDEXED_TITLE = [
    "Select the saved model directory path",
    "Select the label map file path",
    "Select the test data path"
]

_MSG_END_OF_PREDICTION = ' '

UI_EVENT_SAVED_MODEL_LOAD_FAILED = 0
UI_EVENT_SAVED_MODEL_LOAD_SUCCESS = 1
UI_EVENT_PREDICTION_STARTED = 2
UI_EVENT_PREDICTION_END_WITH_FAILED = 3
UI_EVENT_PREDICTION_END_WITH_SUCCESS = 4
UI_EVENT_PREDICTION_PROGRESS_VALUE = 5


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self, parent=None):
        super(QtWidgets.QMainWindow, self).__init__()
        self.setupUi(self)
        self._config = Config()
        self._config.check_default()
        self._is_started = False
        self._latest_result = None
        self._elapsed_mills = None

        self._worker = TestWorker(self, config=self._config)
        self._worker.sig_result.connect(self.slot_test_result)
        self._worker.sig_ui_event.connect(self.slot_ui_event)

        self._ui_binding()
        self._ui_action_binding()
        self._update_whole_path_label()
        self._update_slider()

        self._get_current_model_path_name()

    def _ui_binding(self):
        self.btnStartStop.clicked.connect(self.slot_start_btn)
        self.btnOpenSavedModelPath.clicked.connect(
            self.slot_open_saved_model_path_btn)
        self.btnOpenLabelMapPath.clicked.connect(
            self.slot_open_label_map_path_btn)
        self.btnOpenTestDataPath.clicked.connect(
            self.slot_open_test_data_path_btn)
        self.btnShowResult.clicked.connect(self.slot_show_result_btn)
        self.btnShowResult.setEnabled(False)
        self.sliderThreshold.valueChanged.connect(
            self.slot_slider_value_changed)
        self.sliderThreshold.sliderReleased.connect(self.slot_slider_released)

    def _ui_action_binding(self):
        self.actionOpen_Saved_Model_Path.triggered.connect(
            self.slot_open_saved_model_path_btn)
        self.actionOpen_Labelmap_Path.triggered.connect(
            self.slot_open_label_map_path_btn)
        self.actionOpen_Testdata_Path.triggered.connect(
            self.slot_open_test_data_path_btn)
        self.actionRun.triggered.connect(self.slot_start_btn)
        self.actionResult.triggered.connect(self.slot_show_result_btn)
        self.actionResult.setEnabled(False)
        self.actionExit.triggered.connect(self.slot_exit)

    @QtCore.pyqtSlot(int, int)
    def slot_ui_event(self, ui_event, event_value):
        if UI_EVENT_PREDICTION_PROGRESS_VALUE == ui_event:
            if event_value > 100:
                event_value = 100
            if event_value < 0:
                event_value = 0
            # It is called from UI event signal so it doesn't care of thread issue
            self.progressBar.setValue(event_value)
        elif UI_EVENT_SAVED_MODEL_LOAD_FAILED == ui_event:
            self.slot_log_message("Failed to load the saved model.")
            self.labelStatus.setText("Failed")
        elif UI_EVENT_SAVED_MODEL_LOAD_SUCCESS == ui_event:
            self.slot_log_message("Loaded the saved model successfully.")
        elif UI_EVENT_PREDICTION_STARTED == ui_event:
            self.slot_log_message("Started to predict.")
            self.slot_log_message('Model: ' + self._get_current_model_path_name())
            self.slot_log_message('Threshold: {}%'.format(self._get_cutoff_threshold_value()))
            self._is_started = True
            self.btnStartStop.setEnabled(False)
            self.btnShowResult.setEnabled(False)
            self.actionRun.setEnabled(False)
            self.actionResult.setEnabled(False)
            self._elapsed_mills = time.time()
        elif UI_EVENT_PREDICTION_END_WITH_FAILED == ui_event:
            self.slot_log_message("Failed to predict.")
            self.slot_log_message("Elapsed: {:03.1f}s".format(
                time.time()-self._elapsed_mills))
            self.slot_log_message(_MSG_END_OF_PREDICTION)
            self._is_started = False
            self.btnStartStop.setEnabled(True)
            self.actionRun.setEnabled(True)
            self.labelStatus.setText("Failed")
        elif UI_EVENT_PREDICTION_END_WITH_SUCCESS == ui_event:
            self.slot_log_message("Ended to predict successfully.")
            self.slot_log_message("Elapsed: {:03.1f}s".format(
                time.time()-self._elapsed_mills))
            self.slot_log_message(_MSG_END_OF_PREDICTION)
            self._is_started = False
            self.btnStartStop.setEnabled(True)
            self.btnShowResult.setEnabled(True)
            self.actionRun.setEnabled(True)
            self.actionResult.setEnabled(True)
            self.labelStatus.setText("Success")
        else:
            raise ValueError('There is no method to handle given event')

    @QtCore.pyqtSlot(TestResult)
    def slot_test_result(self, result):
        self.slot_log_message('Test Status: %s' % (
            'Passed' if result.is_passed() else 'Failed'))
        self.slot_log_message('Tested Count : %d' % (result.tested_count))
        self.slot_log_message('Passed Count : %d' % (result.passed_count))
        self._latest_result = result

    @QtCore.pyqtSlot(str)
    def slot_log_message(self, message):
        self.texteditResult.append(message)

    @QtCore.pyqtSlot()
    def slot_start_btn(self):
        if self._config.is_valid():
            self._worker.start()
            self.labelStatus.setText("Processing...")
        else:
            self.slot_log_message(
                'There is no valid configuration for testing, Plaese check configration and try again.')

    @QtCore.pyqtSlot()
    def slot_show_result_btn(self):
        self._showResultDialog()

    @QtCore.pyqtSlot()
    def slot_open_saved_model_path_btn(self):
        old_path = self._config.get(CONFIG_KEY_SAVED_MODEL_PATH)
        selected_path = self._open_directory_select_dialog(
            _PATH_INDEX_SAVED_MODEL,
            old_path)
        self._set_selected_path_to_config(
            _PATH_INDEX_SAVED_MODEL, selected_path)

    @QtCore.pyqtSlot()
    def slot_open_label_map_path_btn(self):
        old_path = self._config.get(CONFIG_KEY_LABEL_MAP_PATH)
        selected_path = self._open_directory_select_dialog(
            _PATH_INDEX_LABEL_MAP,
            old_path)
        self._set_selected_path_to_config(_PATH_INDEX_LABEL_MAP, selected_path)

    @QtCore.pyqtSlot()
    def slot_open_test_data_path_btn(self):
        old_path = self._config.get(CONFIG_KEY_TEST_DATA_PATH)
        selected_path = self._open_directory_select_dialog(
            _PATH_INDEX_TEST_DATA,
            old_path)
        self._set_selected_path_to_config(_PATH_INDEX_TEST_DATA, selected_path)

    @QtCore.pyqtSlot(int)
    def slot_slider_value_changed(self, value):
        self.labelThresholdValue.setText('{}%'.format(value))
        if not self.sliderThreshold.isSliderDown():
            self.slot_slider_released()

    @QtCore.pyqtSlot()
    def slot_slider_released(self):
        slider_value = self.sliderThreshold.value()
        normalized_value = slider_value / 100.0
        self._config.set(CONFIG_KEY_RESULT_CUTOFF_THRESHOLD, normalized_value)
        print('Threshold has changed to {}%'.format(slider_value))

    @QtCore.pyqtSlot()
    def slot_exit(self):
        QtWidgets.QApplication.quit()

    def _showResultDialog(self):
        resultDialog = ResultDialog(self)
        resultDialog.set_test_result(self._latest_result)
        resultDialog.exec_()

    def _open_directory_select_dialog(self, path_index, old_path=None):
        if path_index == _PATH_INDEX_LABEL_MAP:
            selected_path = QtWidgets.QFileDialog.getOpenFileName(
                self, _PATH_INDEXED_TITLE[path_index], old_path)[0]
        else:
            selected_path = QtWidgets.QFileDialog.getExistingDirectory(
                self, _PATH_INDEXED_TITLE[path_index], old_path)

        return selected_path

    def _set_selected_path_to_config(self, path_index, path):
        if path is not None and len(path) > 0:
            if _PATH_INDEX_SAVED_MODEL == path_index:
                self._config.set(key=CONFIG_KEY_SAVED_MODEL_PATH, value=path)
            elif _PATH_INDEX_LABEL_MAP == path_index:
                self._config.set(key=CONFIG_KEY_LABEL_MAP_PATH, value=path)
            elif _PATH_INDEX_TEST_DATA == path_index:
                self._config.set(key=CONFIG_KEY_TEST_DATA_PATH, value=path)

            self._worker.set_config(self._config)

        self._update_selected_path_label(path_index)

    def _update_selected_path_label(self, path_index):
        if _PATH_INDEX_SAVED_MODEL == path_index:
            self.labelSavedModelPath.setText(
                self._config.get(CONFIG_KEY_SAVED_MODEL_PATH))
        elif _PATH_INDEX_LABEL_MAP == path_index:
            self.labelLabelMapPath.setText(
                self._config.get(CONFIG_KEY_LABEL_MAP_PATH))
        elif _PATH_INDEX_TEST_DATA == path_index:
            self.labelTestDataPath.setText(
                self._config.get(CONFIG_KEY_TEST_DATA_PATH))

    def _update_whole_path_label(self):
        for index in range(len(_PATH_INDEXED_TITLE)):
            self._update_selected_path_label(index)

    def _update_slider(self):
        thres_value = self._get_cutoff_threshold_value()
        self.sliderThreshold.setValue(thres_value)

    def _get_cutoff_threshold_value(self):
        thres_value = self._config.get(
            CONFIG_KEY_RESULT_CUTOFF_THRESHOLD, get_type=float)
        normalized_value = int(thres_value * 100)
        return normalized_value

    def _get_current_model_path_name(self):
        saved_model_path = self._config.get(CONFIG_KEY_SAVED_MODEL_PATH)
        if 'saved_model' in saved_model_path:
            # remove saved model
            saved_model_path = saved_model_path[:saved_model_path.find('/saved_model')]
        
        path_list = saved_model_path.split('/')
        if 'export' in path_list[-1]:
            return path_list[-2] + '/' + path_list[-1]
        else:
            return path_list[-1]


 

