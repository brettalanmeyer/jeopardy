from flask import Flask, render_template, session, request
from flask.ext.assets import Environment, Bundle
from flask_socketio import SocketIO, emit

app = Flask(__name__)
assets = Environment(app)
app.config.from_pyfile("config.cfg")
socketio = SocketIO(app, async_mode = "gevent")

@app.route("/")
def index():
	return render_template("home.html")

if __name__ == "__main__":
	socketio.run(app, debug = app.config["DEBUG"], host = app.config["HOST"], port = app.config["PORT"])
