from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.sql import func


Base = declarative_base()

# sqlite:///relative/path/to/file.db
engine = create_engine("sqlite:///database.db", echo=False)
if not database_exists(engine.url):
    create_database(engine.url)


class User(Base):
    """
    Single user can have many rooms which
    again can have many users (admins)
    """
    __tablename__ = "users"

    name = Column(String, primary_key=True)
    password = Column(String)
    # admin property can be accessed via room class
    rooms = relationship("AdminAssociation")

    def __repr__(self):
        return "<User(name='{}', password='{}')>".format(self.name, self.password)


class Room(Base):
    __tablename__ = "rooms"

    name = Column(String, primary_key=True)
    password = Column(String)
    queue = relationship("Song", back_populates="room", cascade="all, delete-orphan")

    def __repr__(self):
        return "<Room(name='{}', password='{}')>".format(self.name, self.password)


class Song(Base):
    """
    A song can be played in many rooms
    and a room can have many songs in queue.
    """
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    song_id = Column(String)
    name = Column(String)
    added = Column(DateTime(timezone=True), default=func.now())
    room = relationship("Room", back_populates="queue")
    room_name = Column(String, ForeignKey("rooms.name"))


class AdminAssociation(Base):
    __tablename__ = "adminassociation"
    user_name = Column(String, ForeignKey('users.name'), primary_key=True)
    room_name = Column(String, ForeignKey('rooms.name'), primary_key=True)
    room = relationship("Room")
