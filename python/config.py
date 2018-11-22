# Containing configuration data for testing
from PyQt5.QtCore import QSettings

CONFIG_KEY_SAVED_MODEL_PATH = 'saved_model_path'
CONFIG_KEY_LABEL_MAP_PATH = 'label_map_path'
CONFIG_KEY_TEST_DATA_PATH = 'test_data_path'

CONFIG_KEY_RESULT_CUTOFF_THRESHOLD = 'result_cutoff_thres'


# Store configuration (Singleton)
class Config(object):

    def __init__(self):
        self._settings = QSettings('TestSuite/Config')

    def get(self, key, get_type=str):
        return self._settings.value(key, type=get_type)

    def set(self, key, value):
        self._settings.setValue(key, value)

    def is_valid(self):
        return (
            self.get(CONFIG_KEY_LABEL_MAP_PATH) is not None and
            self.get(CONFIG_KEY_SAVED_MODEL_PATH) is not None and
            self.get(CONFIG_KEY_TEST_DATA_PATH) is not None)

    def check_default(self):
        if not self._settings.contains(CONFIG_KEY_RESULT_CUTOFF_THRESHOLD):
            self.set(CONFIG_KEY_RESULT_CUTOFF_THRESHOLD, 0.5)
