from hashlib import sha512, md5
from flask import request
from public_queue.models import Room
import datetime


def get_cookie_matching_room(room):
    room_hash = sha512(room.name.encode("utf-8")).hexdigest()
    password_hash = sha512(room.password.encode("utf-8")).hexdigest()
    return {
        "name": room_hash,
        "value": password_hash
    }


def get_admin_cookie_matching_room(room):
    room_hash = sha512(md5(room.name.encode("utf-8")).hexdigest().encode("utf-8")).hexdigest()[::-1]
    password_hash = sha512(md5(room.password.encode("utf-8")).hexdigest().encode("utf-8")).hexdigest()
    return {
        "name": room_hash,
        "value": password_hash
    }


def add_cookie_to_response(response, cookie, admin=False):
    """
    :param response: response object to which the cookie will be bound to
    :param cookie: a dict in the form of {'name': 'cookie name', 'value': 'some value'}
    :param admin: determines how long the cookie will be valid
    :return: response that was given as parameter
    """
    expiration = datetime.datetime.now()
    if admin:
        # Expiration in 10 years
        expiration += datetime.timedelta(days=365 * 10)
    else:
        expiration += datetime.timedelta(hours=12)
    if cookie["value"] not in request.cookies:
        response.set_cookie(cookie["name"], cookie["value"], expires=expiration)
    return response


def get_user_rooms(session):
    """
    :param session: session that we use to query all the room instances
    :return: all rooms that match the users cookies
    """
    rooms = {"user": [], "admin": []}
    for room in session.query(Room).all():
        cookie_user = get_cookie_matching_room(room)
        cookie_admin = get_admin_cookie_matching_room(room)
        if cookie_user["name"] in request.cookies and \
                cookie_user["value"] == request.cookies.get(cookie_user["name"]):
            rooms["user"].append(room)
        print(request.cookies.get(cookie_admin["name"]))
        print(cookie_admin["value"])
        if cookie_admin["name"] in request.cookies and \
                cookie_admin["value"] == request.cookies.get(cookie_admin["name"]):
            rooms["admin"].append(room)
    return rooms

