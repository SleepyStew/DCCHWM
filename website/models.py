from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
class User(db.Model, UserMixin):
    id = db.Column(db.String(64), primary_key=True, index=True)
    sbID = db.Column(db.Integer, unique=True)
    date = db.Column(db.DateTime, default=func.now())
    sbCookie = db.Column(db.String(64))