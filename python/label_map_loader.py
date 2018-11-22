
class LabelMapLoader(object):
    def __init__(self, filepath=None):
        self._label_map = dict()

        if filepath is not None:
            self.load(filepath)

    def load(self, filepath):
        self._label_map.clear()

        with open(filepath, 'r') as f:
            lines = f.readlines()
            item_id = None
            for line in lines:
                line = line.strip()
                if 'id:' in line:
                    item_id = int(line[line.find('id:')+3:].strip())
                if 'name:' in line:
                    item_name = line[line.find(
                        'name:')+5:].strip().replace('\'', '')
                    if item_id is not None:
                        self._label_map[item_id] = item_name
                    item_id = None
                    item_name = None

    def get_label_name_by_id_index(self, id_index):
        if id_index < 0 or id_index > self.get_classes_count():
            raise ValueError('Out of bound with given index [{}]'.format(id_index))

        return self._label_map[id_index]

    def get_id_index_by_label_name(self, label_name):
        return (list(self._label_map.keys())[list(self._label_map.values()).index(label_name)])

    def get_classes_count(self):
        return len(self._label_map)

    def is_valid(self):
        return len(self._label_map) > 0
