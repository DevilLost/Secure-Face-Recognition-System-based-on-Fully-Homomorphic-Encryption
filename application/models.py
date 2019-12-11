# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_status = db.Column(db.Integer)
    user_upload = db.Column(db.Integer)
    user_id = db.Column(db.String(29), nullable=False)
    create_time = db.Column(db.DateTime)
