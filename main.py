from website import create_app
import sys

sys.dont_write_bytecode = True

app = create_app()

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if __name__ == '__main__':
    from waitress import serve
    serve(app, port=30015, host="0.0.0.0")
