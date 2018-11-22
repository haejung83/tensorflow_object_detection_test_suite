r"""Convert raw dataset to TFRecord for object_detection.

# Before execute this script move this file to the object detection's dataset_tools directory

Example usage:
  python object_detection/dataset_tools/create_raw_dataset_to_tf_record.py \
  --label_map_path=/some directories/label_map/label_map.pbtxt \
  --data_dir=/some directories/image_data
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import hashlib
import io
import logging
import os
import sys

from lxml import etree
import PIL.Image
import tensorflow as tf

from object_detection.utils import dataset_util
from object_detection.utils import label_map_util
from random import shuffle

flags = tf.app.flags
flags.DEFINE_string(
    'data_dir', '', 'Root directory to ShinhanCard dataset.')
flags.DEFINE_string('label_map_path', 'data/pascal_label_map.pbtxt',
                    'Path to label map proto')
flags.DEFINE_boolean('ignore_difficult_instances', False, 'Whether to ignore '
                     'difficult instances')
FLAGS = flags.FLAGS

# Added
ENABLE_SHUFFLE_IMAGE_LIST = True


def dict_to_tf_example(data,
                       img_path,
                       label_map_dict,
                       ignore_difficult_instances=False):

    with tf.gfile.GFile(img_path, 'rb') as fid:
        encoded_jpg = fid.read()
    encoded_jpg_io = io.BytesIO(encoded_jpg)
    image = PIL.Image.open(encoded_jpg_io)
    if image.format != 'JPEG':
        raise ValueError('Image format not JPEG')
    key = hashlib.sha256(encoded_jpg).hexdigest()

    width = int(data['size']['width'])
    height = int(data['size']['height'])

    xmin = []
    ymin = []
    xmax = []
    ymax = []
    classes = []
    classes_text = []
    truncated = []
    poses = []
    difficult_obj = []
    if 'object' in data:
        for obj in data['object']:
            difficult = bool(int(obj['difficult']))
            if ignore_difficult_instances and difficult:
                continue

            difficult_obj.append(int(difficult))

            xmin.append(float(obj['bndbox']['xmin']) / width)
            ymin.append(float(obj['bndbox']['ymin']) / height)
            xmax.append(float(obj['bndbox']['xmax']) / width)
            ymax.append(float(obj['bndbox']['ymax']) / height)
            classes_text.append(obj['name'].encode('utf8'))
            classes.append(label_map_dict[obj['name']])
            truncated.append(int(obj['truncated']))
            poses.append(obj['pose'].encode('utf8'))

    example = tf.train.Example(features=tf.train.Features(feature={
        'image/height': dataset_util.int64_feature(height),
        'image/width': dataset_util.int64_feature(width),
        'image/filename': dataset_util.bytes_feature(
            data['filename'].encode('utf8')),
        'image/source_id': dataset_util.bytes_feature(
            data['filename'].encode('utf8')),
        'image/key/sha256': dataset_util.bytes_feature(key.encode('utf8')),
        'image/encoded': dataset_util.bytes_feature(encoded_jpg),
        'image/format': dataset_util.bytes_feature('jpeg'.encode('utf8')),
        'image/object/bbox/xmin': dataset_util.float_list_feature(xmin),
        'image/object/bbox/xmax': dataset_util.float_list_feature(xmax),
        'image/object/bbox/ymin': dataset_util.float_list_feature(ymin),
        'image/object/bbox/ymax': dataset_util.float_list_feature(ymax),
        'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        'image/object/class/label': dataset_util.int64_list_feature(classes),
        'image/object/difficult': dataset_util.int64_list_feature(difficult_obj),
        'image/object/truncated': dataset_util.int64_list_feature(truncated),
        'image/object/view': dataset_util.bytes_list_feature(poses),
    }))
    return example


def get_image_name_list(image_path):
    files_no_ext = [".".join(f.split(".")[:-1])
                    for f in os.listdir(image_path)]

    if files_no_ext is None or len(files_no_ext) == 0:
        raise ValueError('There is no images')

    return files_no_ext


def main(_):
    data_dir = FLAGS.data_dir

    label_map_dict = label_map_util.get_label_map_dict(FLAGS.label_map_path)

    # 80 percent of the minimal count
    train_set_percent_factor = 0.8

    card_data_list = []

    images_dir = os.path.join(data_dir, 'images')
    annotations_dir = os.path.join(data_dir, 'annotations')

    # Build whole card data
    card_list = os.listdir(images_dir)
    for card_name in card_list:
        card_path = os.path.join(images_dir, card_name)
        card_image_list = get_image_name_list(card_path)
        card_image_count = len(card_image_list)

        if ENABLE_SHUFFLE_IMAGE_LIST:
            shuffle(card_image_list)

        card_data_list.append({
            'card_name': card_name,
            'image_list': card_image_list,
            'count': card_image_count,
            'train_count': round(card_image_count * train_set_percent_factor),
            'eval_count': card_image_count - round(card_image_count * train_set_percent_factor)
        })

    train_writer = tf.python_io.TFRecordWriter('card_train.record')
    eval_writer = tf.python_io.TFRecordWriter('card_eval.record')

    for card_data in card_data_list:
        card_name = card_data['card_name']
        card_image_count = card_data['count']
        card_train_image_count = card_data['train_count']
        card_eval_image_count = card_data['eval_count']


        print('Converting card code with [%s]' % (card_name))
        print('Count of training images [%d]' % (card_train_image_count))
        print('Count of evaluation images [%d]' % (card_eval_image_count))

        for index, card_image_name in enumerate(card_data['image_list']):
            if index % 100 == 0:
                print('On image %d of %d' % (index, card_image_count))

            path = os.path.join(
                annotations_dir, card_name, card_image_name + '.xml')
            with tf.gfile.GFile(path, 'r') as fid:
                xml_str = fid.read()
            xml = etree.fromstring(xml_str)
            annotation_data = dataset_util.recursive_parse_xml_to_dict(xml)[
                'annotation']

            image_sub_path = os.path.join(
                images_dir, card_name, card_image_name + '.JPG')

            if index < card_train_image_count:
                tf_train_example = dict_to_tf_example(annotation_data,
                                                      image_sub_path,
                                                      label_map_dict,
                                                      FLAGS.ignore_difficult_instances)
                train_writer.write(tf_train_example.SerializeToString())
            else:
                tf_eval_example = dict_to_tf_example(annotation_data,
                                                     image_sub_path,
                                                     label_map_dict,
                                                     FLAGS.ignore_difficult_instances)
                eval_writer.write(tf_eval_example.SerializeToString())

    train_writer.close()
    eval_writer.close()

    total_train_image_count = 0
    total_eval_image_count = 0
    for card_data in card_data_list:
        total_train_image_count = total_train_image_count + card_data['train_count']
        total_eval_image_count = total_eval_image_count + card_data['eval_count']

    print('Total training image count [%d]' %(total_train_image_count))
    print('Total evaluation image count [%d]' %(total_eval_image_count))

    print('Done')


if __name__ == '__main__':
    tf.app.run()
