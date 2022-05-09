from flask import Flask, flash, session
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate

db = SQLAlchemy()
DB_NAME = "schoolbox.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'u6KRp3dN8ePKcXduEOYB5TQz3KUTmQS7FVJ1QEtk5rr445kBF5dw3J7dYub1epDh'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    print("[?] Setup config and initialised database.")

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    print ("[?] Setup Login Manager")

    from .models import User, Note
    
    @login_manager.user_loader
    def load_user(id):
        user = User.query.filter_by(id=id).first()
        return user

    from .views import views
    from .auth import auth
    from .api import api
    from .views import MyAdminIndexView, DefaultModelView

    admin = Admin(app, index_view=MyAdminIndexView())
    admin.add_view(DefaultModelView(User, db.session))
    admin.add_view(DefaultModelView(Note, db.session))

    print("[?] Setup Admin Panel")

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')
    app.register_blueprint(api, url_prefix='/api/')

    print("[?] Setup Page Blueprints")

    migrate = Migrate(app, db)
    
    create_database(app)

    return app
    

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print("[?] Created database.")