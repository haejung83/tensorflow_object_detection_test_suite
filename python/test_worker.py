
from PyQt5 import QtCore

import numpy as np
import cv2
import os
import json

from PIL import Image
from config import Config
from config import CONFIG_KEY_SAVED_MODEL_PATH
from config import CONFIG_KEY_LABEL_MAP_PATH
from config import CONFIG_KEY_TEST_DATA_PATH
from label_map_loader import LabelMapLoader
from test_result import TestResult, TestResultGroup, TestResultImage, TestResultClass
from test_session import TestSession
import test_session
import mainwindow


class TestWorker(QtCore.QThread):
    sig_result = QtCore.pyqtSignal(TestResult)
    sig_ui_event = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self._config = config
        self._session = TestSession(config=config)
        self._label_map_loader = LabelMapLoader()
        self._test_groups = dict()

        # Make connection between worker and session
        self._session.sigTestSessionStatus.connect(self.log_session_status)
        self._session.sigTestSessionResult.connect(self.log_session_result)
        self._session.sigTestSessionCount.connect(self.log_session_count)

    def set_config(self, config):
        self._config = config
        self._session.set_config(config)

    def get_config(self):
        return self._config

    def start(self, loop=False):
        super().start(QtCore.QThread.LowPriority)

    def stop(self):
        raise NotImplementedError(
            'stop() method not implemented, It is not necessary')

    def _prepare(self):
        if self._config is None:
            raise ValueError('There is no exist the config for preparing')

        self._load_saved_model()
        self._load_label_map()
        self._build_test_group()

    def _load_label_map(self):
        label_map_path = self._config.get(CONFIG_KEY_LABEL_MAP_PATH)
        if label_map_path is not None and len(label_map_path) > 0:
            self._label_map_loader.load(label_map_path)
        else:
            raise ValueError("There is no path to get the label map file")

    def _load_saved_model(self):
        saved_model_path = self._config.get(CONFIG_KEY_SAVED_MODEL_PATH)
        if saved_model_path is not None:
            self._session.loadSavedModel(saved_model_path)
        else:
            raise ValueError("There is no path to get the saved model")

    # Only support jpeg image
    def _build_test_group(self):
        # Check validation
        test_data_path = self._config.get(CONFIG_KEY_TEST_DATA_PATH)
        if test_data_path is None or len(test_data_path) == 0:
            raise ValueError("There is no path to get the test data")

        # Clear old test group
        self._test_groups.clear()

        # Retrieve group by directory name
        test_groups = [name for name in os.listdir(test_data_path)
                       if os.path.isdir(os.path.join(test_data_path, name))]

        # Build test data and classes in each group
        for group_name in test_groups:
            self._test_groups[group_name] = {'results': []}
            image_file_list = os.listdir(
                os.path.join(test_data_path, group_name))
            image_file_list = list(
                filter(lambda image_file: image_file.lower().endswith(".jpg"), image_file_list))
            if image_file_list is not None and len(image_file_list) > 0:
                image_file_list.sort()
                self._test_groups[group_name].update(
                    {'test_data': image_file_list})
            else:
                del self._test_groups[group_name]
                continue

            with open(os.path.join(test_data_path, group_name, 'classes.json'), mode='r', encoding='utf-8') as f:
                loaded_classes = json.load(f)
                self._test_groups[group_name].update(
                    {'classes': loaded_classes['classes']})

    def run(self):
        # print('Run TestWorker')
        # Prepare
        self._prepare()
        data_path = self._config.get(CONFIG_KEY_TEST_DATA_PATH)
        # Prediction with test group data
        self._session.slot_predict_group(data_path, self._test_groups)

    def log_session_status(self, value: int):
        if test_session.SESSION_STATUS_LOAD_SUCCESS == value:
            self.sig_ui_event.emit(
                mainwindow.UI_EVENT_SAVED_MODEL_LOAD_SUCCESS, 0)
        elif test_session.SESSION_STATUS_LOAD_FAILED == value:
            self.sig_ui_event.emit(
                mainwindow.UI_EVENT_SAVED_MODEL_LOAD_FAILED, 0)
        elif test_session.SESSION_STATUS_PREDICTION_STARTED == value:
            self.sig_ui_event.emit(mainwindow.UI_EVENT_PREDICTION_STARTED, 0)
        elif test_session.SESSION_STATUS_PREDICTION_SUCCESS == value:
            self.sig_result.emit(self._bulid_test_result())
            self.sig_ui_event.emit(
                mainwindow.UI_EVENT_PREDICTION_END_WITH_SUCCESS, 0)
        elif test_session.SESSION_STATUS_PREDICTION_FAILED == value:
            self.sig_ui_event.emit(
                mainwindow.UI_EVENT_PREDICTION_END_WITH_FAILED, 0)

    def log_session_result(self, value):
        for result_key, result_value in value.items():
            self._test_groups[result_key]['results'] = result_value

    def log_session_count(self, count, total_count):
        percent = int((count / total_count)*100)
        self.sig_ui_event.emit(
            mainwindow.UI_EVENT_PREDICTION_PROGRESS_VALUE, percent)

    def _bulid_test_result(self):
        passed_count = 0
        tested_count = 0

        result = TestResult()
        result.group = list()

        test_data_path = self._config.get(CONFIG_KEY_TEST_DATA_PATH)

        for group_name, group_data in self._test_groups.items():
            result_group = TestResultGroup()
            result_group.name = group_name
            result_group.required_classes = self._get_names_by_labels(
                group_data['classes'])
            result_group.images = list()

            set_of_required_classes = set(group_data['classes'])
            non_passed_group = False

            for test_file_name, prediction_result in zip(group_data['test_data'], group_data['results']):
                result_image = TestResultImage()
                result_image.name = test_file_name
                result_image.filepath = os.path.join(
                    test_data_path, group_name, test_file_name)
                result_image.classes = list()

                for label, score, box in zip(prediction_result['detection_classes'], prediction_result['detection_scores'], prediction_result['detection_boxes']):
                    result_class = TestResultClass()
                    result_class.name = self._get_name_by_label(label)
                    result_class.label = label.tolist()  # ndarray to list
                    result_class.score = score.tolist()  # ndarray to list
                    result_class.box = box.tolist()     # ndarray to list
                    result_image.classes.append(result_class)

                if len(set_of_required_classes-set(prediction_result['detection_classes'].tolist())) == 0:
                    passed_count = passed_count + 1
                else:
                    non_passed_group = True

                result_image.sort_classes()
                result_group.images.append(result_image)
                tested_count = tested_count + 1

            if non_passed_group:
                # Append to front
                result.group.insert(0, result_group)
            else:
                result.group.append(result_group)

        result.passed_count = passed_count
        result.tested_count = tested_count

        return result

    def _get_name_by_label(self, label):
        return self._label_map_loader.get_label_name_by_id_index(int(label))

    def _get_names_by_labels(self, labels):
        new_labels = list()

        labels.sort()
        for label in labels:
            new_labels.append(self._get_name_by_label(label))

        return new_labels
