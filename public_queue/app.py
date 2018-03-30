from flask import Flask, request, render_template, \
    redirect, url_for, flash, jsonify, json
from flask_login import LoginManager, login_required, current_user
from sqlalchemy.orm import sessionmaker
from hashlib import sha256
from public_queue.models import Room, engine, Song, User
from public_queue.secret_keys import secret_key, wtf_csrf_secret_key
import builtins
import sqlalchemy

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY=secret_key,
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
    if name in map(lambda n: n[0], session.query(Room.name).all()):
        return False
    room = Room(name=name, password=password)
    session.add(room)
    session.commit()
    print("New Room instance added to our database")
    return True


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
        if name in map(lambda n: n[0], session.query(Room.name).all()) and password == real_password:
            return redirect("rooms/{}".format(name))
        error = "Invalid password."
    return render_template("login.html", error=error, rooms=get_rooms())


@app.route("/rooms/<name>", methods=["POST", "GET"])
def room(name=None):
    session = Session()
    room = next(r for r in session.query(Room).all() if r.name == name)
    if request.method == "POST":
        song_id = request.form.get("song_id")
        song_name = request.form.get("song_name")
        if song_id is None:
            # Here we got a response to our response
            pass
        else:
            song = Song(song_id=song_id, name=song_name)
            try:
                session.add(song)
                room.queue.append(song)
                session.commit()
                data = "success"
                response = app.response_class(
                    response=data,  # json.dumps(data),
                    status=200,
                    mimetype="application/json"
                )
                return response
            except (builtins.TypeError, sqlalchemy.exc.IntegrityError) as e:
                print(e)
                data = "fail"
                response = app.response_class(
                    response=data,  # json.dumps(data),
                    status=200,
                    mimetype="application/json"
                )
                return response
    return render_template("room.html", room=room, songs=room.queue)


@app.route("/rooms/<name>/admin", methods=["POST", "GET"])
def admin_page(name=None):
    room = next(r for r in get_rooms() if r.name == name)
    return render_template("admin.html", room=room, songs=room.queue)


@app.route("/rooms/<name>/admin/delete/<song_id>", methods=["POST"])
def delete_song(name=None, song_id=None):
    session = Session()
    room = next(r for r in session.query(Room.name).all() if r.name == name)
    song = session.query(Song).filter(Song.song_id == song_id and Song.room == room)
    song = next(s for s in song.all())
    print(song)
    session.delete(song)
    session.commit()
    return jsonify(response="song deleted")
    # song = session.query(Song).filter(Song.room == room and Song.song_id == song_id).all()
    # session.delete(song)


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
    user = None
    if current_user.is_authenticated: 
        user = current_user
    return render_template("index.html", user=user, error=error)


@app.route("/login", methods=["POST", "GET"])
def user_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if password is not None and username is not None:
            password = sha256(password.encode("ascii")).hexdigest()
            session = Session()
            actual_user = session.query(User).filter(User.name == username)[0]
            if password == actual_user.password and username == actual_user.name:
                print("\nTODO: log the user in\n")
                return redirect("/")
        return redirect(url_for('index', error="Login failed."))
    return render_template("user-login.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    password_confirmation = request.form.get("confirm-password")
    error = ""
    if password is not None and password == password_confirmation and len(password) > 3:
        encoded_password = sha256(password.encode("ascii")).hexdigest()
        session = Session()
        if username in map(lambda name: name[0], session.query(User.name).all()):
            error += "User with that name already exists. "
        new_user = User(password=encoded_password, name=username)
        session.add(new_user)
        session.commit()
        print("Successfully created new user.")
        return redirect("/")
    print("Failed to create new user.")
    if password == password_confirmation:
        error += "Passwords did not match. "
    if password is None or len(password) > 3:
        error += "Password was too short."
    return redirect(url_for("user_login", error=""))


@login_manager.user_loader
def user_loader(user_id):
    pass
