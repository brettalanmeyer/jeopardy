from flask import Flask, render_template, session, request, Response, redirect
from flask.ext.assets import Environment, Bundle
from flask_socketio import SocketIO, emit
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from flask.ext.session import Session
from datetime import datetime
import json

app = Flask(__name__)
assets = Environment(app)
app.config.from_pyfile("config.cfg")
socketio = SocketIO(app, async_mode = "gevent")

SESSION_TYPE = "filesystem"
app.config.from_object(__name__)
Session(app)

engine = create_engine("mysql+mysqldb://" + app.config["MYSQL_USERNAME"] + ":" + app.config["MYSQL_PASSWORD"] + "@" + app.config["MYSQL_HOST"] + "/" + app.config["MYSQL_DATABASE"], pool_recycle = 3600)
db_session = scoped_session(sessionmaker(autocommit = False, autoflush = False, bind = engine))
SessionMaked = sessionmaker(bind = engine)
db = SessionMaked()
Base = declarative_base()

class Player(Base):

	__tablename__ = "players"

	id = Column(Integer, primary_key = True)
	name = Column(String(255))
	characterId = Column(Integer, ForeignKey("characters.id"))
	character = relationship("Character")
	createdAt = Column(DateTime)

	def __init__(self, name, createdAt):
		self.name = name
		self.createdAt = createdAt


class Character(Base):

	__tablename__ = "characters"

	id = Column(Integer, primary_key = True)
	name = Column(String(255))
	image = Column(String(255))
	createdAt = Column(DateTime)

	def __init__(self, name, image, createdAt):
		self.name = name
		self.image = image
		self.createdAt = createdAt


class Answer(Base):

	__tablename__ = "answers"

	id = Column(Integer, primary_key = True)
	createdAt = Column(DateTime)

	def __init__(self, createdAt):
		self.createdAt = createdAt


class Category(Base):

	__tablename__ = "categories"

	id = Column(Integer, primary_key = True)
	name = Column(String(255))
	createdAt = Column(DateTime)

	def __init__(self, name, createdAt):
		self.name = name
		self.createdAt = createdAt


class Game(Base):

	__tablename__ = "games"

	id = Column(Integer, primary_key = True)
	createdAt = Column(DateTime)

	def __init__(self, createdAt):
		self.createdAt = createdAt

class Host(Base):

	__tablename__ = "hosts"

	id = Column(Integer, primary_key = True)
	createdAt = Column(DateTime)

	def __init__(self, createdAt):
		self.createdAt = createdAt


@app.route("/activate-reset/")
def activate_reset():
	socketio.emit("receive-reset", None, broadcast = True)
	return redirect("/reset/")

@app.route("/reset/")
def reset():
	db.query(Game).delete()
	db.query(Host).delete()
	db.query(Player).delete()
	db.commit()
	session.clear()
	return redirect("/")

@app.route("/")
def page_index():
	return render_template("main.html", entity = session.get("entity", ""))

@app.route("/home/")
def page_home_index():
	return render_template("home/index.html", entityData = getEntityData())

@app.route("/board/")
def page_board_index():
	db.add(Game(datetime.now()))
	db.commit()
	setEntity("board")
	players = db.query(Player)
	return render_template("board/index.html", players = players)

@app.route("/host/")
def page_host_index():
	db.add(Host(datetime.now()))
	db.commit()
	setEntity("host")
	return "host"

@app.route("/player/")
def page_player():
	player = Player(None, datetime.now())
	db.add(player)
	db.commit()
	session["playerId"] = player.id
	setEntity("player" + str(db.query(Player).count() + 1))
	return render_template("player/name.html")

@app.route("/player/", methods = ["POST"])
def page_player_create():
	return json_response({ "id": player.id })

@app.route("/player/character/")
def page_player_character():
	characters = db.query(Character)
	return render_template("player/character.html", characters = characters)


@app.after_request
def beforeRequest(response):
	db.close()
	return response

def setEntity(entity):
	session["entity"] = entity
	socketio.emit("receive-main-entity", getEntityData(), broadcast = True)

def getEntityData():
	return {
		"hasBoard": db.query(Game).count() == 1,
		"hasHost": db.query(Host).count() == 1,
		"hasPlayer1": db.query(Player).count() >= 1,
		"hasPlayer2": db.query(Player).count() >= 2,
		"hasPlayer3": db.query(Player).count() >= 3
	}

def json_response(data):
	return Response(json.dumps(data), status = 200, mimetype = "application/json")

if __name__ == "__main__":
	socketio.run(app, debug = app.config["DEBUG"], host = app.config["HOST"], port = app.config["PORT"])

# return session.get("key", "not set")
