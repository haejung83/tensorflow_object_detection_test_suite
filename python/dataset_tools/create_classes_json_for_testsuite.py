r"""Create classes.json file for the TestSuite.

# Before execute this script move this file to the object detection's dataset_tools directory

Example usage:
  python object_detection/dataset_tools/create_classes_json_for_testsuite.py \
  --label_map_path=/mnt/data/datasets/ShinhanCard_78/180820_final_image/label_map/label_map.pbtxt \
  --data_dir=/mnt/data/datasets/ShinhanCard_78/180820_final_image \
  --out_dir=/mnt/data/datasets/ShinhanCard_78/classes_out
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import hashlib
import io
import logging
import os
import sys
import json

from lxml import etree
import PIL.Image
import tensorflow as tf

from object_detection.utils import dataset_util
from object_detection.utils import label_map_util
from random import shuffle

flags = tf.app.flags
flags.DEFINE_string('data_dir', '', 'Root directory to ShinhanCard dataset.')
flags.DEFINE_string('out_dir', '', 'Directory to created classes file')
flags.DEFINE_string('label_map_path', 'data/pascal_label_map.pbtxt',
                    'Path to label map proto')
FLAGS = flags.FLAGS


def get_list_of_class(annotation_data, label_map_dict):
    classes = []
    classes_text = []
    if 'object' in annotation_data:
        for obj in annotation_data['object']:
            classes_text.append(obj['name'].encode('utf8'))
            classes.append(label_map_dict[obj['name']])

    return classes_text, classes


def get_image_name_list(image_path):
    files_no_ext = [".".join(f.split(".")[:-1])
                    for f in os.listdir(image_path)]

    if files_no_ext is None or len(files_no_ext) == 0:
        raise ValueError('There is no images')

    return files_no_ext


def main(_):
    data_dir = FLAGS.data_dir
    out_dir = FLAGS.out_dir

    label_map_dict = label_map_util.get_label_map_dict(FLAGS.label_map_path)

    card_data_list = []

    images_dir = os.path.join(data_dir, 'images')
    annotations_dir = os.path.join(data_dir, 'annotations')

    # Build whole card data
    card_list = os.listdir(images_dir)
    for card_name in card_list:
        card_path = os.path.join(images_dir, card_name)
        card_image_list = get_image_name_list(card_path)
        card_image_count = len(card_image_list)

        card_data_list.append({
            'card_name': card_name,
            'image_list': card_image_list,
            'count': card_image_count
        })

    # Create directories with card_name in out_dir
    for card_name in card_list:
        card_class_path = os.path.join(out_dir, card_name)
        if not os.path.exists(card_class_path):
            os.makedirs(card_class_path)

    # Generate classes.json file to each matched directory
    for card_data in card_data_list:
        card_name = card_data['card_name']
        card_image_count = card_data['count']
        print('Generating card code with [%s]' % (card_name))

        first_card_image_name = card_data['image_list'][0]
        path = os.path.join(annotations_dir, card_name, first_card_image_name + '.xml')
        with tf.gfile.GFile(path, 'r') as fid:
            xml_str = fid.read()
        xml = etree.fromstring(xml_str)
        annotation_data = dataset_util.recursive_parse_xml_to_dict(xml)['annotation']

        _, classes = get_list_of_class(annotation_data, label_map_dict)

        # Sort before write
        classes.sort()

        dict_clasess = { 'classes': classes }
        create_filepath = os.path.join(out_dir, card_name, 'classes.json')
        with open(create_filepath, 'w') as fp:
            dumped = json.dumps(dict_clasess)
            print(dumped)
            fp.write(dumped)

    print('\nDone')


if __name__ == '__main__':
    tf.app.run()
