from website import create_app
from flask import Flask
import sys

sys.dont_write_bytecode = True

app = create_app()
socketio = app[1]

if __name__ == '__main__':
    from waitress import serve
    print("[✔] Finished setting up webserver!")
    print("[?] Running webserver...")
    socketio.run(app)
    # serve(app, port=30015, host="0.0.0.0")
