from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'u6KRp3dN8ePKcXduEOYB5TQz3KUTmQS7FVJ1QEtk5rr445kBF5dw3J7dYub1epDh'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/auth/')

    return app