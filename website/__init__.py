from datetime import datetime
from os import environ
from os import path

from dotenv import load_dotenv, find_dotenv
from flask import Flask
from flask_admin import Admin
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

load_dotenv(find_dotenv())

db = SQLAlchemy()
migrate = Migrate(db)
DB_NAME = "schoolbox.db"


def create_app():
    global limiter, app, socketio
    app = Flask(__name__)
    socketio = SocketIO(app)
    app.config['SECRET_KEY'] = environ.get("SECRET_KEY")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.url_map.strict_slashes = False
    db.init_app(app)
    csrf = CSRFProtect()
    csrf.init_app(app)  # Compliant
    print("[?] Setup config and initialised database.")

    limiter = Limiter(app=app, key_func=get_remote_address, default_limits=["60/minute"])

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    print("[?] Setup Login Manager")

    from .models import User, Note, Message

    @login_manager.user_loader
    def load_user(id):
        user = User.query.filter_by(id=id).first()
        return user

    from .views import views
    from .auth import auth
    from .api import api
    from .pwa import pwa
    from .views import MyAdminIndexView, DefaultModelView

    admin = Admin(app, index_view=MyAdminIndexView())
    admin.add_view(DefaultModelView(User, db.session))
    admin.add_view(DefaultModelView(Note, db.session))
    admin.add_view(DefaultModelView(Message, db.session))

    print("[?] Setup Admin Panel")

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')
    app.register_blueprint(api, url_prefix='/api/')
    app.register_blueprint(pwa, url_prefix='/')

    print("[?] Setup Page Blueprints")

    migrate = Migrate(app, db, render_as_batch=True)

    create_database(app)

    return [app, socketio]


def create_database(app):
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print("[?] Created database.")


def audit_log(audit):
    print(audit)
    with open('audit.log', 'a') as file:
        file.write(f"{datetime.now()} | {audit}\n")
