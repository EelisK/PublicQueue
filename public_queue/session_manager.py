from hashlib import sha512
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


def add_cookie_to_response(response, cookie):
    """
    :param response: response object to which the cookie will be bound to
    :param cookie: a dict in the form of {'name': 'cookie name', 'value': 'some value'}
    :return: response that was given as parameter
    """
    expiration = datetime.datetime.now()
    expiration += datetime.timedelta(hours=12)
    response.set_cookie(cookie["name"], cookie["value"], expires=expiration)
    return response


def get_user_rooms(session):
    """
    :param session: session that we use to query all the room instances
    :return: all rooms that match the users cookies
    """
    rooms = []
    for room in session.query(Room).all():
        cookie = get_cookie_matching_room(room)
        if cookie["name"] in request.cookies and cookie["value"] == request.cookies.get(cookie["name"]):
            rooms.append(room)
    return rooms
