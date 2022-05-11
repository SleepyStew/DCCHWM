from website import create_app
from flask import Flask
import sys

sys.dont_write_bytecode = True

app = create_app()

if __name__ == '__main__':
    from waitress import serve
    register_template_filters(flask_app=app)
    print("[✔] Finished setting up webserver!")
    print("[?] Running webserver...")
    serve(app, port=30015, host="0.0.0.0")
    
def register_template_filters(flask_app: Flask) -> None:
    from website.filters import custom_template_filters
    flask_app.register_blueprint(custom_template_filters.blueprint)
    return None
