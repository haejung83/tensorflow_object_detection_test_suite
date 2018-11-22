
from PyQt5 import QtCore

import tensorflow as tf
import numpy as np
import cv2
import os
from PIL import Image

from config import Config
from config import CONFIG_KEY_RESULT_CUTOFF_THRESHOLD

# Constants for status of this session
SESSION_STATUS_LOAD_FAILED = 0
SESSION_STATUS_LOAD_SUCCESS = 1
SESSION_STATUS_PREDICTION_STARTED = 2
SESSION_STATUS_PREDICTION_FAILED = 3
SESSION_STATUS_PREDICTION_SUCCESS = 4


def _create_encoded_image_string(image_array_np, encoding_format):
    od_graph = tf.Graph()
    with od_graph.as_default():
        if encoding_format == 'jpg':
            encoded_string = tf.image.encode_jpeg(image_array_np)
        elif encoding_format == 'png':
            encoded_string = tf.image.encode_png(image_array_np)
        else:
            raise ValueError(
                'Supports only the following formats: `jpg`, `png`')
    with tf.Session(graph=od_graph):
        return encoded_string.eval()


class TestSession(QtCore.QObject):
    sigTestSessionStatus = QtCore.pyqtSignal(int)
    sigTestSessionCount = QtCore.pyqtSignal(int, int)
    sigTestSessionResult = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self._graph = None
        self._config = config

    def set_config(self, config):
        self._config = config

    def loadSavedModel(self, saved_model_path):
        self.reset()
        # Load the saved model from file
        try:
            self._graph = tf.Graph()
            tf_config = tf.ConfigProto()
            tf_config.gpu_options.per_process_gpu_memory_fraction = 0.2
            with tf.Session(graph=self._graph, config=tf_config) as sess:
                tf.saved_model.loader.load(sess, ["serve"], saved_model_path)
                # Get handles to input and output tensors
                ops = tf.get_default_graph().get_operations()
                all_tensor_names = {
                    output.name for op in ops for output in op.outputs}

                self._tensor_dict = {}
                for key in ['num_detections', 'detection_boxes', 'detection_scores',
                            'detection_classes', 'detection_masks']:
                    tensor_name = key + ':0'
                    if tensor_name in all_tensor_names:
                        self._tensor_dict[key] = tf.get_default_graph(
                        ).get_tensor_by_name(tensor_name)

                self._image_tensor = tf.get_default_graph().get_tensor_by_name(
                    'encoded_image_string_tensor:0')

            self.sigTestSessionStatus.emit(SESSION_STATUS_LOAD_SUCCESS)
        except:
            self.sigTestSessionStatus.emit(SESSION_STATUS_LOAD_FAILED)

    def reset(self):
        self._graph = None
        tf.reset_default_graph()

    # Predict just an image
    @QtCore.pyqtSlot(np.ndarray)
    def slot_predict(self, input_data: np.ndarray):
        if self._graph is None:
            self.sigTestSessionStatus.emit(SESSION_STATUS_PREDICTION_FAILED)
            return
        try:
            with self._graph.as_default():
                with tf.Session() as sess:
                    self.sigTestSessionStatus.emit(
                        SESSION_STATUS_PREDICTION_STARTED)

                    # Encode to image string
                    jpg_image_str = _create_encoded_image_string(
                        input_data, 'jpg')

                    # Run inference
                    output_dict = sess.run(self._tensor_dict, feed_dict={
                        self._image_tensor: [jpg_image_str]})

                    # all outputs are float32 numpy arrays, so convert types as appropriate
                    output_dict['num_detections'] = int(
                        output_dict['num_detections'][0])
                    output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(
                        np.uint8)
                    output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                    output_dict['detection_scores'] = output_dict['detection_scores'][0]

                    self.sigTestSessionStatus.emit(
                        SESSION_STATUS_PREDICTION_SUCCESS)
                    self.sigTestSessionResult.emit(output_dict)
        except:
            self.sigTestSessionStatus.emit(SESSION_STATUS_PREDICTION_FAILED)

    # Predict with group of images
    @QtCore.pyqtSlot(str, dict)
    def slot_predict_group(self, data_path: str, test_group: dict):
        if self._graph is None:
            self.sigTestSessionStatus.emit(SESSION_STATUS_PREDICTION_FAILED)
            return

        self.sigTestSessionStatus.emit(SESSION_STATUS_PREDICTION_STARTED)

        try:
            with self._graph.as_default():
                with tf.Session() as sess:
                    total_image_count = self._get_total_image_count(test_group)
                    current_image_count = 0
                    cutoff_thres = 0.5
                    if self._config:
                        cutoff_thres = self._config.get(
                            CONFIG_KEY_RESULT_CUTOFF_THRESHOLD, get_type=float)

                    ret_dict = dict()
                    for group_name, group_data in test_group.items():
                        ret_result = []
                        if not 'test_data' in group_data:
                            continue

                        for image_file in group_data['test_data']:
                            # Read raw jpeg image and convert to ndarray
                            image_data = np.asarray(Image.open(
                                os.path.join(data_path, group_name, image_file)))
                            # Encode to image string
                            jpg_image_str = _create_encoded_image_string(
                                image_data, 'jpg')
                            # Run inferenc
                            output_dict = sess.run(self._tensor_dict, feed_dict={
                                self._image_tensor: [jpg_image_str]})

                            # all outputs are float32 numpy arrays, so convert types as appropriate
                            output_dict['num_detections'] = int(
                                output_dict['num_detections'][0])
                            output_dict['detection_classes'] = output_dict['detection_classes'][0].astype(
                                np.uint8)
                            output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                            output_dict['detection_scores'] = output_dict['detection_scores'][0]

                            ret_result.append(
                                self._filter_result_by_thres(output_dict, thres=cutoff_thres))

                            current_image_count = current_image_count + 1
                            self.sigTestSessionCount.emit(
                                current_image_count, total_image_count)

                        ret_dict[group_name] = ret_result

                    self.sigTestSessionResult.emit(ret_dict)
            self.sigTestSessionStatus.emit(SESSION_STATUS_PREDICTION_SUCCESS)
        except:
            self.sigTestSessionStatus.emit(SESSION_STATUS_PREDICTION_FAILED)

    def _filter_result_by_thres(self, source_dict, thres=0.5):
        filtered_dict = dict()
        scores = source_dict['detection_scores']
        separate_index = -1
        for index, score in enumerate(scores):
            if score < thres:
                separate_index = index
                break

        if separate_index != -1:
            filtered_dict['num_detections'] = separate_index
            filtered_dict['detection_classes'] = source_dict['detection_classes'][:separate_index]
            filtered_dict['detection_boxes'] = source_dict['detection_boxes'][:separate_index]
            filtered_dict['detection_scores'] = source_dict['detection_scores'][:separate_index]

        return filtered_dict

    def _get_total_image_count(self, test_group):
        total_image_count = 0
        for _, group_data in test_group.items():
            if 'test_data' in group_data:
                total_image_count = total_image_count + \
                    len(group_data['test_data'])

        return total_image_count
