from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy_utils import database_exists, create_database


Base = declarative_base()

# sqlite:///relative/path/to/file.db
engine = create_engine("sqlite:///database.db", echo=True)
if not database_exists(engine.url):
    create_database(engine.url)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    # admin property can be accessed via room class
    rooms = relationship("User", backref="admin")

    def __repr__(self):
        return "<User(id='{}', name='{}', password='{}')>".format(self.id, self.name, self.password)


class Room(Base):
    __tablename__ = "rooms"

    name = Column(String, primary_key=True)
    password = Column(String)

    def __repr__(self):
        return "<Room(name='{}', password='{}')>".format(self.name, self.password)

Base.metadata.create_all(engine)
