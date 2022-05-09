from website import create_app
import sys

sys.dont_write_bytecode = True

app = create_app()

if __name__ == '__main__':
    from waitress import serve
    print("[✔] Finished setting up webserver!")
    print("[?] Running webserver...")
    serve(app, port=30015, host="0.0.0.0")
