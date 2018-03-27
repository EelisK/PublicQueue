from flask import Flask, request, render_template, \
    redirect, url_for, session, flash
from flask_login import LoginManager, login_required, current_user
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from hashlib import sha256
from youtube_queue.models import Room, engine
from youtube_queue.forms import LoginForm
from youtube_queue.secret_keys import secret_key, wtf_csrf_secret_key


app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY= secret_key,
    WTF_CSRF_SECRET_KEY=wtf_csrf_secret_key
))
login_manager = LoginManager()
login_manager.init_app(app)
Session = sessionmaker(bind=engine)


def get_rooms():
    session = Session()
    return session.query(Room).all()

def insert_room(name, password):
    password = sha256(password.encode("ascii")).hexdigest()
    session = Session()
    for elem in session.query(Room.name).all():
        print(elem)
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


@app.route("/rooms", methods=["GET", "POST"])
def room_login():
    error = None
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        password = sha256(password.encode("ascii")).hexdigest()
        session = Session()
        real_password = session.query(Room.password).filter(Room.name == name).first()[0]
        print("{}".format(real_password))
        print("{}".format(password))
        if name in map(lambda name: name[0], session.query(Room.name).all()) and password == real_password:
            return redirect("rooms/{}".format(name))
        error="Invalid password."
    return render_template("login.html", error=error, rooms=get_rooms())


@app.route("/rooms/<name>", methods=["POST", "GET"])
def room(name=None):
    # TODO: add song to queue
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
        if current_user.is_authenticated or True:
            return render_template("room-creation.html")
        else:
            return redirect(url_for(".index", error="Login required to create rooms."))


@app.route("/")
def index():
    error = request.args.get("error")
    request.args = {}
    navigation = []
    navigation.append({"caption": "log in to a room", "href": "/rooms"})
    navigation.append({"caption": "create a room", "href": "/room-creation"})
    user = {}
    if current_user.is_authenticated: 
        user["name"] = current_user.username
    else: 
        user["name"] = ""
    return render_template("index.html", user=user, navigation=navigation, error=error)


@app.route("/login", methods=["POST", "GET"])
def user_login():
    if request.method == "POST":
        form = LoginForm()
        if form.validate_on_submit():
            flash("Successfully logged in as %s" % form.user.username)
            session['user_id'] = form.user.id
            return redirect(url_for('index'))
        print("unsuccessfully validated")
        return redirect(url_for('index', error="Login failed."))
    return render_template("user-login.html")


@login_manager.user_loader
def user_loader(user_id):
    pass
