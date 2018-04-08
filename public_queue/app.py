from flask import Flask, request, render_template, \
    redirect, url_for, flash, jsonify, json, make_response
from flask_login import LoginManager, login_required, current_user
from sqlalchemy.orm import sessionmaker
from hashlib import sha256
from public_queue.models import Room, engine, Song, User
from public_queue.secret_keys import secret_key, wtf_csrf_secret_key
from public_queue import session_manager, thumbnail_manager
import builtins
import sqlalchemy
import jinja2

app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY=secret_key,
    WTF_CSRF_SECRET_KEY=wtf_csrf_secret_key
))
login_manager = LoginManager()
login_manager.init_app(app)
Session = sessionmaker(bind=engine)


def get_rooms(session):
    return session.query(Room).all()


def insert_room(name, password):
    password = sha256(password.encode("ascii")).hexdigest()
    session = Session()
    if name in map(lambda n: n[0], session.query(Room.name).all()):
        return False, None
    room = Room(name=name, password=password)
    session.add(room)
    session.commit()
    print("New Room instance added to our database")
    return True, room


@app.route("/rooms", methods=["GET", "POST"])
def room_login():
    error = None
    session = Session()
    # Login on POST
    if request.method == "POST":
        name = request.form.get("room-name")
        password = request.form.get("password")
        password = sha256(password.encode("ascii")).hexdigest()
        try:
            real_password = next(r for r in session.query(Room).filter(Room.name == name)).password
        except StopIteration:
            print("Room does not exist")
            return redirect(url_for("index", error="You tried to log in to a room that does not exist"))
        if name in map(lambda n: n[0], session.query(Room.name).all()) and password == real_password:
            # Set user cookie
            response = make_response(redirect("rooms/{}".format(name)))
            room = next(r for r in session.query(Room).filter(Room.name == name))
            user_cookie = session_manager.get_cookie_matching_room(room)
            response = session_manager.add_cookie_to_response(response, user_cookie)
            return response
        error = "Invalid password."
    return custom_render_template(session, "login.html", error=error, rooms=get_rooms(session))


@app.route("/rooms/<name>", methods=["POST", "GET"])
def room(name=None):
    session = Session()
    try:
        room = next(r for r in session.query(Room).all() if r.name == name)
    except StopIteration:
        return render_template("404.html")
    cookie = session_manager.get_cookie_matching_room(room)
    # Check that user has already logged in by looking at their cookies
    if cookie["name"] not in request.cookies or cookie["value"] != request.cookies.get(cookie["name"]):
        return redirect(url_for("room_login", error="You need to log in before you can enter a room"))
    # Post a song to rooms queue
    if request.method == "POST":
        song_id = request.form.get("song_id")
        song_name = request.form.get("song_name")
        thumbnail_url = request.form.get("thumbnail_url")
        duration = request.form.get("duration")
        if song_id is None:
            # Here we got a response to our response
            pass
        else:
            song = Song(song_id=song_id, name=song_name, thumbnail=thumbnail_url, duration=duration)
            try:
                session.add(song)
                # Check if this song was the first and if it was add its id to the room
                if len(room.queue) == 0:
                    room.current_song_id = song.id
                room.queue.append(song)
                session.commit()
                data = "success"
                response = app.response_class(
                    response=data,  # json.dumps(data),
                    status=200,
                    mimetype="application/json"
                )

                # Download thumbnail
                thumbnail_manager.download_thumbnail(thumbnail_url, song_id)

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
    return custom_render_template(session, "room.html", room=room, songs=room.queue)


@app.route("/rooms/<name>/admin", methods=["POST", "GET"])
def admin_page(name=None):
    session = Session()
    room = next(r for r in get_rooms(session) if r.name == name)
    admin_cookie = session_manager.get_admin_cookie_matching_room(room)
    if admin_cookie["name"] not in request.cookies or \
            admin_cookie["value"] != request.cookies.get(admin_cookie["name"]):
        return redirect(url_for("index", error="You are not admin."))
    first_id = None
    if len(room.queue) > 0:
        first_id = room.queue[0].song_id
    return custom_render_template(session, "admin.html", room=room, songs=room.queue, first_id=first_id)


@app.route("/rooms/<name>/admin/delete/<song_id>", methods=["POST"])
def delete_song(name=None, song_id=None):
    session = Session()
    id = request.form.get("id")
    print("\nid: {}\n".format(id))
    room = next(r for r in session.query(Room.name).all() if r.name == name)
    song = session.query(Song).filter(Song.song_id == song_id and Song.room == room and Song.id == id)
    song = next(s for s in song.all())
    print(song)
    session.delete(song)
    session.commit()
    try:
        next_id = (next(r for r in session.query(Room).all() if r.name == name)).queue[0].song_id
    except IndexError:
        next_id = None
    return jsonify(response=next_id)


@app.route("/rooms/<name>/admin/play/<song_id>", methods=["POST"])
def change_song(name=None, song_id=None):
    session = Session()
    id = request.form.get("id")
    print(request.form)
    print(request)
    room = session.query(Room).filter(Room.name == name)[0]
    try:
        print("song id: {}\n".format(id))
        song = next(s for s in session.query(Song).filter(Song.id > id))
        print("SONG:\n")
        print(song)
        print("\n")
        print("\n\nNext song id: {}\n\n".format(song.id))
        room.current_song_id = song.id
        session.commit()
        return jsonify(response=song.song_id)
    except StopIteration as e:
        # There was no next song
        return jsonify(response=str(e))


@app.route("/room-creation", methods=["POST"])
def create_room():
    session = Session()
    if request.method == "POST":
        name = request.form.get("room-name")
        password = request.form.get("password")
        password_re = request.form.get("confirm-password")
        if " " in name or "\t" in name or "\n" in name:
            return custom_render_template(session, "room-creation.html", error="Room name cannot contain spaces.")
        if password != password_re:
            return custom_render_template(session, "room-creation.html", error="Passwords did not match.")
        # If insert is successful redirect to room url
        insert_successful, room = insert_room(name, password)
        if insert_successful:
            response = make_response(redirect("/rooms/{}".format(name)))
            cookie = session_manager.get_cookie_matching_room(room)
            response = session_manager.add_cookie_to_response(response, cookie, admin=True)
            admin_cookie = session_manager.get_admin_cookie_matching_room(room)
            response = session_manager.add_cookie_to_response(response, admin_cookie, admin=True)
            return response
        else:
            return custom_render_template(session, "room-creation.html", error="Room with that name exists already.")
    else:
        if current_user.is_authenticated or True:
            return custom_render_template(session, "room-creation.html")
        else:
            return redirect(url_for("index", error="Login required to create rooms."))


@app.route("/")
def index():
    error = request.args.get("error")
    user = None
    session = Session()
    if current_user.is_authenticated: 
        user = current_user
    return custom_render_template(session, "index.html", user=user, error=error, rooms=get_rooms(session))


@app.route("/login", methods=["POST", "GET"])
def user_login():
    session = Session()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if password is not None and username is not None:
            password = sha256(password.encode("utf-8")).hexdigest()
            session = Session()
            try:
                actual_user = session.query(User).filter(User.name == username)[0]
            except IndexError:
                return redirect(url_for('user_login', error="User does not exist"))
            if password == actual_user.password and username == actual_user.name:
                print("\nTODO: log the user in\n")
                return redirect("/")
        return redirect(url_for('user_login', error="Login failed."))
    return custom_render_template(session, "login.html", error=request.args.get("error"), rooms=get_rooms(session))


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    password_confirmation = request.form.get("confirm-password")
    error = ""
    print(password)
    print(password_confirmation)
    print(username)
    if password is not None and password == password_confirmation and len(password) > 3:
        encoded_password = sha256(password.encode("utf-8")).hexdigest()
        session = Session()
        if username in map(lambda name: name[0], session.query(User.name).all()):
            error += "User with that name already exists. "
        new_user = User(password=encoded_password, name=username)
        session.add(new_user)
        session.commit()
        print("Successfully created new user.")
        return redirect("/")
    print("Failed to create new user.")
    if password != password_confirmation:
        error += "Passwords did not match. "
    if password is None or len(password) < 3:
        error += "Password was too short."
    return redirect(url_for("user_login", error=error))


@login_manager.user_loader
def user_loader(user_id):
    pass


def custom_render_template(session, *args, **kwargs):
    return render_template(*args, **kwargs, my_rooms=session_manager.get_user_rooms(session))


def format_seconds(number):
    minutes = number // 60
    seconds = number % 60
    return "{}:{:02d}".format(minutes, seconds)


def current_song(room):
    session = Session()
    try:
        return session.query(Song).filter(Song.id == room.current_song_id)[0]
    except IndexError:
        return None


jinja2.filters.FILTERS["format_seconds"] = format_seconds
jinja2.filters.FILTERS["current_song"] = current_song

