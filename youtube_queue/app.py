from flask import Flask, request, render_template, redirect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from hashlib import sha256
from .models import Room, engine


app = Flask(__name__)
Session = sessionmaker(bind=engine)


def get_rooms():
    session = Session()
    return session.query(Room).all()
    """
    # Old:
    return rooms
    """

def insert_room(name, password):
    password = sha256(password.encode("ascii")).hexdigest()
    session = Session()
    if name in session.query(Room.name).all():
        return False
    room = Room(name=name, password=password)
    session.add(room)
    session.commit()
    print("New Room instance added to our database")
    return True
    """
    if name not in map(lambda room: room["name"], rooms):
        room = {}
        room["name"] = name
        room["password"] = password
        room["users"] = 0
        room["songs"] = []
        rooms.append(room)
    """


def room_login(name, password):
    password = sha256(password.encode("ascii")).hexdigest()
    session = Session()
    if name in session.query(Room.name).filter(Room.name == name) and \
        password == session.query(Room.password).filter(Room.name == name).first():
        # Maybe add user to Room
        return redirect("rooms/{}".format(name))
    else:
        return render_template("login.html", error="Invalid password.", rooms=get_rooms())


@app.route("/rooms", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        return room_login(name, password)
    else:
        return render_template("login.html", rooms=get_rooms())


@app.route("/rooms/<name>", methods=["POST", "GET"])
def room(name=None):
    """
    if request.method == "POST":
        pass
    elif True:
        pass
    else:
        pass
    """
    room = next(room for room in get_rooms() if room.name == name)
    return render_template("room.html", room=room)


@app.route("/room-creation", methods=["POST", "GET"])
def create_room():
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        # If insert is successful redirect to room url
        if insert_room(name, password):
            return redirect("/rooms/{}".format(name))
        else:
            return render_template("room-creation.html", error="Room with that name exists already.")
    else:
        return render_template("room-creation.html")


@app.route("/")
def index():
    navigation = []
    navigation.append({"caption": "log in to a room", "href": "/rooms"})
    navigation.append({"caption": "create a room", "href": "/room-creation"})
    user = {}
    user["name"] = "Eelis"  # TODO: get actual username
    return render_template("index.html", user=user, navigation=navigation)
