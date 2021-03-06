from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.String(64), primary_key=True, index=True)
    sbID = db.Column(db.Integer, unique=True)
    date = db.Column(db.DateTime, default=func.now())
    sbCookie = db.Column(db.String(64))
    notes = db.relationship('Note')
    setting_alerts = db.Column(db.String(64), default='high')
    setting_deleted_messages = db.Column(db.String(64), default='hide')
    setting_timestamp_hour_type = db.Column(db.String(64), default='12')
    sbName = db.Column(db.String(128))
    customJavascript = db.Column(db.String(2048), default='')
    isAdmin = db.Column(db.Boolean, default=False)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.sbID'))
    content = db.Column(db.String(512))
    displayOrder = db.Column(db.Integer)
    date = db.Column(db.DateTime(timezone=True), default=func.now())


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    content = db.Column(db.String(1024))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    deleted = db.Column(db.Boolean, default=False)
