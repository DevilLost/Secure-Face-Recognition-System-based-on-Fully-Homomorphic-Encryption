# -*- coding: utf-8 -*-

import os
import copy
import time
import argparse
import numpy as np
from scipy import misc
import tensorflow as tf
from application.face.src.align import detect_face
from application.face.src.facenet import get_model_filenames, prewhiten

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
model_path = './application/face/src/20180408-102900'
graph = tf.get_default_graph()
session = tf.Session()
try:
    model_exp = os.path.expanduser(model_path)
    meta_file, ckpt_file = get_model_filenames(model_exp)
    saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file), input_map=None)
    saver.restore(session, os.path.join(model_exp, ckpt_file))
    images_placeholder = graph.get_tensor_by_name("input:0")
    embeddings = graph.get_tensor_by_name("embeddings:0")
    phase_train_placeholder = graph.get_tensor_by_name("phase_train:0")
except Exception as e:
    print(e)
    exit(1)


def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('image_files', type=str, nargs='+', help='Images to compare')
    parser.add_argument('--image_size', type=int,
                        help='Image size (height, width) in pixels.', default=160)
    parser.add_argument('--margin', type=int,
                        help='Margin for the crop around the bounding box (height, width) in pixels.', default=44)
    parser.add_argument('--gpu_memory_fraction', type=float,
                        help='Upper bound on the amount of GPU memory that will be used by the process.', default=1.0)
    return parser.parse_args(argv)


def load_and_align_data(image_paths, image_size, margin, gpu_memory_fraction):
    minsize = 20  # minimum size of face
    threshold = [0.6, 0.7, 0.7]  # three steps's threshold
    factor = 0.709  # scale factor
    with tf.Graph().as_default():
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with sess.as_default():
            pnet, rnet, onet = detect_face.create_mtcnn(sess, None)

    tmp_image_paths = copy.copy(image_paths)
    img_list = []
    for image in tmp_image_paths:
        img = misc.imread(os.path.expanduser(image), mode='RGB')
        img_size = np.asarray(img.shape)[0:2]
        bounding_boxes, _ = detect_face.detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
        if len(bounding_boxes) < 1:
            image_paths.remove(image)
            print("can't detect face, remove ", image)
            continue
        det = np.squeeze(bounding_boxes[0, 0:4])
        bb = np.zeros(4, dtype=np.int32)
        bb[0] = np.maximum(det[0] - margin / 2, 0)
        bb[1] = np.maximum(det[1] - margin / 2, 0)
        bb[2] = np.minimum(det[2] + margin / 2, img_size[1])
        bb[3] = np.minimum(det[3] + margin / 2, img_size[0])
        cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
        aligned = misc.imresize(cropped, (image_size, image_size), interp='bilinear')
        prewhitened = prewhiten(aligned)
        img_list.append(prewhitened)
    images = np.stack(img_list)
    return images


def get_user_data(filename, type):
    origin_data_path = './application/data/originUserFaceData/'
    img_path = './upload/' + filename + '.' + type + '.png'
    args = parse_arguments([img_path])
    time_start = time.time()
    print('开始处理:' + filename + '.' + type)
    images = load_and_align_data(args.image_files, args.image_size, args.margin, args.gpu_memory_fraction)
    with graph.as_default():
        with session.as_default() as sess:
            feed_dict = {images_placeholder: images, phase_train_placeholder: False}
            emb = sess.run(embeddings, feed_dict=feed_dict)
            np.savetxt(origin_data_path + filename + '.' + type + '.txt', emb[0])
    time_end = time.time()
    print('处理结束:' + filename + '.' + type + ',耗时:', end='')
    print('%.2f' % (time_end - time_start))
    if os.access(origin_data_path + filename + '.' + type + '.txt', os.F_OK):
        return True
    return False


if __name__ == '__main__':
    args = parse_arguments(['./face/src/20180408-102900', './face/src/q2.jpg'])
