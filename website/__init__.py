from flask import Flask, flash, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
DB_NAME = "schoolbox.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'u6KRp3dN8ePKcXduEOYB5TQz3KUTmQS7FVJ1QEtk5rr445kBF5dw3J7dYub1epDh'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User, Note
    
    @login_manager.user_loader
    def load_user(id):
        user = User.query.filter_by(id=id).first()
        return user

    from .views import views
    from .auth import auth
    from .api import api

    app.register_blueprint(views, url_prefix='/')
    admin = Admin(app, index_view=views.admin_index())
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Note, db.session))
    app.register_blueprint(auth, url_prefix='/auth/')
    app.register_blueprint(api, url_prefix='/api/')
    
    create_database(app)

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print("Created database.")