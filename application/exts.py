# -*- coding: utf-8 -*-

import os
import gzip
import base64
import numpy as np


# 图片后缀类型判断
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png']


# 获取原始数据
def get_origin_data(user_id):
    path = './application/data/originUserFaceData/'
    if os.path.exists(path + "%s.old.txt" % user_id):
        face_data_a = np.loadtxt(path + user_id + '.old.txt', delimiter=",")
        face_data_b = face_data_a.tolist()
        return face_data_b
    else:
        return None


# 获取加密数据
def get_encrypt_data(user_id):
    path = './application/data/encryptUserFaceData/'
    if os.path.exists(path + '%s.old' % user_id):
        with open(path + '%s.old' % user_id, "rb") as f:
            encrypt_res = f.read()
        encrypt_res = str(base64.b64encode(gzip.compress(encrypt_res)))
        return encrypt_res
    else:
        return None
