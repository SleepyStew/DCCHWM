from . import db
from sqlalchemy.sql import func
from flask_login import UserMixin
import jinja2
class User(db.Model, UserMixin):
    id = db.Column(db.String(64), primary_key=True, index=True)
    sbID = db.Column(db.Integer, unique=True)
    date = db.Column(db.DateTime, default=func.now())
    sbCookie = db.Column(db.String(64))
    notes =  db.relationship('Note')
    setting_alerts = db.Column(db.String(64), default='high')

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('user.sbID'))
    content = db.Column(db.String(512))
    date = db.Column(db.DateTime(timezone=True), default=func.now())

    def html_content(self):
        # Escape, then convert newlines to br tags, then wrap with Markup object
        # so that the <br> tags don't get escaped.
        def escape(s):
            # unicode() forces the conversion to happen immediately,
            # instead of at substitution time (else <br> would get escaped too)
            return unicode(jinja2.escape(s))
        return jinja2.Markup(escape(self.content).replace('\n', '<br>'))