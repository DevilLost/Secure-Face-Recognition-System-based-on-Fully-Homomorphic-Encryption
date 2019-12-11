# -*- coding: utf-8 -*-

import os
import time
import base64
import string
import random
import config
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from application.models import User, db
from application.exts import allowed_file, get_origin_data, get_encrypt_data
from application.face_data import get_user_data
from application.detect import load_and_detect_data
from application.util import face_compares, gen_user_key, data_encrypt
from flask import render_template, request, jsonify, session, redirect


def create_app():
    app = Flask(__name__)  # type: Flask
    app.config.from_object(config)
    db.init_app(app)
    CSRFProtect(app)
    return app


app = create_app()


# 首页
@app.route('/')
def index():
    if request.cookies.get('user_id') is not None:
        session['user_id'] = request.cookies.get('user_id')
    elif session.get('user_id') is None:
        session.permanent = True
        session['user_id'] = time.strftime("%Y%m%d%H%M%S", time.localtime()) + ''.join(
            random.choices(string.ascii_letters + string.digits, k=15))
    return render_template('index.html')


# 录入
@app.route('/gain')
def gain():
    if session.get('user_id') is None:
        return redirect('/')
    return render_template('gain.html')


# 信息
@app.route('/info')
def information():
    if session.get('user_id') is None:
        return redirect('/')
    img_status = False
    user_img = ''
    if os.path.exists("./upload/%s.old.png" % session.get('user_id')):
        user_img = '/upload/' + session.get('user_id') + '.old.png'
        img_status = True
    return render_template('info.html', user_id=session.get('user_id'), user_img=user_img, img_status=img_status)


# 关于
@app.route('/about')
def about():
    return render_template('about.html')


# 获取照片
@app.route('/upload/<filename>', methods=['GET'])
def upload(filename):
    user_id = session.get('user_id')
    req_user_id = request.cookies.get('user_id')
    if user_id is None:
        return redirect('/')
    if user_id + '.old.png' != filename:
        return redirect('/')
    if req_user_id is None:
        return redirect('/')
    if req_user_id + '.old.png' != filename:
        return redirect('/')
    if os.path.exists("./upload/%s" % filename):
        file = os.path.join('./upload', filename)
        with open(file, 'rb') as f:
            img = f.read()
        return img
    return render_template('404.html'), 404


# 文件上传接口
@app.route('/file_upload', methods=['POST'])
def file_upload():
    if 'file' not in request.files:
        return jsonify('false'), 403
    res = {'code': 0, 'msg': '禁止'}
    user_id = session.get('user_id')
    image = request.files['file']
    header_type = request.headers.get('Type')
    key_res = False

    if image and allowed_file(image.filename):
        img_path = './upload/' + user_id + '.png'
        if header_type == '1':
            img_path = './upload/' + user_id + '.old.png'
            # 生成key
            key_res = gen_user_key(user_id)
        if header_type == '2':
            img_path = './upload/' + user_id + '.new.png'
        try:
            image.save(os.path.join(img_path))
        except Exception as e:
            print(e)
            res['msg'] = '系统错误0'
            return jsonify(res), 200
        # 人脸有无判断
        try:
            result = load_and_detect_data([img_path], 1.0)
        except Exception as e:
            print(e)
            res['msg'] = '系统错误1'
            return jsonify(res), 200
        if result == 0:
            os.remove(img_path)
            res['msg'] = '未识别到人脸'
            return jsonify(res), 200
        if header_type == '1' and not key_res:
            res = {'code': 0, 'msg': '密钥生成失败'}
            return jsonify(res), 200
        # 数据入库
        db_res = User.query.filter(User.user_id == user_id).first()
        if db_res is None:
            user = User(user_status=1, user_id=user_id, user_upload=1,
                        create_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            db.session.add(user)
            db.session.commit()
        elif header_type == '1':
            user = User.query.filter(User.user_id == user_id).first()
            user.user_upload += 1
            user.user_status = 1
            db.session.add(user)
            db.session.commit()
        res['code'] = 1
        res['msg'] = '上传成功'
        res['user_id'] = user_id
        return jsonify(res), 200
    else:
        return jsonify(res), 200


# 拍照上传接口
@app.route('/img_upload', methods=['POST'])
def img_upload():
    base64_image = request.form['image']
    base64_image = base64_image.replace('data:image/png;base64,', '')
    user_id = session.get('user_id')
    img_path = './upload/' + user_id + '.old.png'
    res = {'code': 0, 'msg': '禁止'}
    with open(img_path, "wb") as file:
        decode_base64 = base64.b64decode(base64_image)
        file.write(decode_base64)
    # 人脸有无判断
    try:
        result = load_and_detect_data([img_path], 1.0)
    except Exception as e:
        print(e)
        res['msg'] = '系统错误'
        return jsonify(res), 200
    if result == 0:
        os.remove(img_path)
        res['msg'] = '未识别到人脸'
        return jsonify(res), 200
    if not gen_user_key(user_id):
        res['msg'] = '密钥生成失败'
        return jsonify(res), 200
    # 数据入库
    db_res = User.query.filter(User.user_id == user_id).first()
    if db_res is None:
        user = User(user_status=1, user_id=user_id, user_upload=1,
                    create_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    else:
        user = User.query.filter(User.user_id == user_id).first()
        user.user_upload += 1
        user.user_status = 1
    db.session.add(user)
    db.session.commit()
    res['code'] = 1
    res['msg'] = '成功'
    res['user_id'] = user_id
    return jsonify(res), 200


# 脸部比较
@app.route('/face_compare', methods=['POST'])
def face_compare():
    res = {'code': 0, 'msg': '禁止'}
    user_id = session.get('user_id')
    req_user_id = request.cookies.get('user_id')
    if user_id is None:
        return jsonify(res), 200
    if req_user_id is None:
        return jsonify(res), 200
    if user_id != req_user_id:
        res['msg'] = 'ID不一致，请刷新后重新上传'
        return jsonify(res), 200
    if request.form['user_id'] is None:
        res['msg'] = '请刷新后重试'
        return jsonify(res), 200
    if request.form['user_id'] != user_id:
        res['msg'] = 'ID不一致，请刷新后重新上传'
        return jsonify(res), 200
    origin_res = os.path.exists('./application/data/originUserFaceData/%s.old.txt' % user_id)
    try:
        user = User.query.filter(User.user_id == session.get('user_id')).first()
        # 如果已经获取过原始数据 则设置过session['upload_times'] 此时不需要运行获取原始数据 反之则需要
        # 如果又上传了一次照片 则session['upload_times']中的数据应小于数据库中的值 需要运行数据
        if session.get('upload_times') is None or user.user_upload > session.get('upload_times') or not origin_res:
            origin_res = get_user_data(user_id, 'old')
            session['upload_times'] = user.user_upload
        if session.get('upload_times') == user.user_upload and user.user_status >= 3 and os.path.exists(
                './application/data/encryptUserFaceData/%s.old' % user_id):
            encrypt_res = True
        else:
            encrypt_res = data_encrypt(user_id, 'old')
        origin_new_res = get_user_data(user_id, 'new')
        encrypt_new_res = data_encrypt(user_id, 'new')
    except Exception as e:
        print(e)
        res['msg'] = '系统错误2'
        return jsonify(res), 200
    if origin_new_res and encrypt_new_res and origin_res and encrypt_res:
        result = face_compares(user_id)
        print('识别结果:', end='')
        print(result[0])
        # 关键判断部分
        if result[0] > 0.7:
            res['code'] = 2
            res['msg'] = '认证失败'
            res['data'] = "%.4f" % result[0]
        else:
            res['code'] = 1
            res['msg'] = '识别成功'
            res['data'] = "%.4f" % result[0]
    return jsonify(res), 200


# 原始数据处理
@app.route('/origin_data', methods=['POST'])
def origin_data():
    res = {'code': 0, 'msg': '禁止'}
    user_id = session.get('user_id')
    req_user_id = request.cookies.get('user_id')
    if user_id is None:
        return jsonify(res), 200
    if req_user_id is None:
        return jsonify(res), 200
    if user_id != req_user_id:
        res['msg'] = 'ID不一致，请刷新后重新上传'
        return jsonify(res), 200
    origin_res = os.path.exists('./application/data/originUserFaceData/%s.old.txt' % user_id)
    try:
        user = User.query.filter(User.user_id == user_id).first()
        if session.get('upload_times') is None or user.user_upload > session.get('upload_times'):
            origin_res = get_user_data(user_id, 'old')
            session['upload_times'] = user.user_upload
        elif session.get('upload_times') == user.user_upload and user.user_status >= 2 and origin_res:
            res['code'] = 1
            res['msg'] = '成功'
            res['data'] = get_origin_data(user_id)
            return jsonify(res), 200
    except Exception as e:
        print(e)
        res['msg'] = '系统错误3'
        return jsonify(res), 200
    if origin_res:
        try:
            update = User.query.filter(User.user_id == user_id).first()
            update.user_status = 2
            db.session.commit()
        except Exception as e:
            print(e)
            res['msg'] = '系统错误4'
            return jsonify(res), 200
        res['code'] = 1
        res['msg'] = '成功'
        res['data'] = get_origin_data(user_id)
        return jsonify(res), 200
    res['msg'] = '数据已经处理或系统错误'
    return jsonify(res), 200


# 处理加密数据
@app.route('/encrypt_data', methods=['POST'])
def encrypt_data():
    res = {'code': 0, 'msg': '禁止'}
    user_id = session.get('user_id')
    req_user_id = request.cookies.get('user_id')
    if user_id is None:
        return jsonify(res), 200
    if req_user_id is None:
        return jsonify(res), 200
    if user_id != req_user_id:
        res['msg'] = 'ID不一致，请刷新后重试'
        return jsonify(res), 200

    try:
        user = User.query.filter(User.user_id == user_id).first()
        # 如果upload_times为None 或着用户又上传了一次则说明需要获取一次原数据
        if session.get('upload_times') is None or user.user_upload > session.get('upload_times'):
            get_user_data(user_id, 'old')
            session['upload_times'] = user.user_upload
            user.user_status = 2
        # 如果已经有了加密数据
        encrypt_res = os.path.exists('./application/data/encryptUserFaceData/%s.old' % user_id)
        if session.get('upload_times') == user.user_upload and user.user_status >= 3 and encrypt_res:
            res['code'] = 1
            res['msg'] = '成功'
            res['data'] = get_encrypt_data(user_id)
            return jsonify(res), 200
        # 如果没有加密数据，则需要加密数据计算
        origin_res = os.path.exists('./application/data/originUserFaceData/%s.old.txt' % user_id)
        if session.get('upload_times') == user.user_upload and user.user_status >= 2 and origin_res:
            encrypt_res = data_encrypt(user_id, 'old')
            user.user_status = 3
        db.session.commit()
    except Exception as e:
        print(e)
        res['msg'] = '系统错误5'
        return jsonify(res), 200
    if encrypt_res:
        res['code'] = 1
        res['msg'] = '成功'
        res['data'] = get_encrypt_data(user_id)
        return jsonify(res), 200
    return jsonify(res), 200


# 自定义404模板
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# 自定义500模板
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
