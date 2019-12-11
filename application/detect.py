# -*- coding: utf-8 -*-

import os
import copy
from scipy import misc
import tensorflow as tf
from application.face.src.align import detect_face

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def load_and_detect_data(image_paths, gpu_memory_fraction):
    minsize = 20
    threshold = [0.6, 0.7, 0.7]
    factor = 0.709
    with tf.Graph().as_default():
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with sess.as_default():
            pnet, rnet, onet = detect_face.create_mtcnn(sess, None)

    tmp_image_paths = copy.copy(image_paths)
    for image in tmp_image_paths:
        img = misc.imread(os.path.expanduser(image), mode='RGB')
        bounding_boxes, _ = detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
        if len(bounding_boxes) < 1:
            image_paths.remove(image)
            return 0
        else:
            return 1


if __name__ == '__main__':
    print(load_and_detect_data(['./face/src/q2.jpg'], 1.0))
