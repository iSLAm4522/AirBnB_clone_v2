#!/usr/bin/python3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from os import getenv
from models.base_model import BaseModel, Base
from models.user import User
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.review import Review


classes = {
    'User': User, 'Place': Place,
    'State': State, 'City': City, 'Amenity': Amenity,
    'Review': Review
}


class DBStorage:
    __engine = None
    __session = None

    def __init__(self):
        """
        Initialize a new DBStorage instance
        """
        dialect = 'mysql'
        driver = 'mysqldb'
        HBNB_MYSQL_USER = getenv('HBNB_MYSQL_USER')
        HBNB_MYSQL_PWD = getenv('HBNB_MYSQL_PWD')
        HBNB_MYSQL_HOST = getenv('HBNB_MYSQL_HOST')
        HBNB_MYSQL_DB = getenv('HBNB_MYSQL_DB')
        HBNB_ENV = getenv('HBNB_ENV')
        # dialect+driver://username:password@host:port/database
        self.__engine = create_engine('{}+{}://{}:{}@{}/{}'.format(
            dialect, driver, HBNB_MYSQL_USER, HBNB_MYSQL_PWD,
            HBNB_MYSQL_HOST, HBNB_MYSQL_DB), pool_pre_ping=True)

        if HBNB_ENV == 'test':
            Base.metadata.drop_all(bind=self.__engine)

    def reload(self):
        """Reloads data from the database"""
        try:
            Base.metadata.create_all(self.__engine)
            session_factory = sessionmaker(bind=self.__engine,
                                           expire_on_commit=False)
            self.__session = scoped_session(session_factory)
        except Exception as e:
            # If database connection fails, print warning but don't crash
            print("Warning: Database connection failed. Error: {}".format(e))
            print("Console will start but database operations will not work.")
            self.__session = None

    def all(self, cls=None):
        """Query on the current database session"""
        dictionary = {}
        if self.__session is None:
            return dictionary
        if cls:
            objects = self.__session.query(cls).all()
            for obj in objects:
                dictionary["{}.{}".format(type(obj).__name__, obj.id)] = obj
        else:
            for cls in classes.values():
                objects = self.__session.query(cls).all()
                for obj in objects:
                    dictionary[
                        "{}.{}".format(type(obj).__name__, obj.id)] = obj
        return dictionary

    def new(self, obj):
        """Adds a new object to the current database session"""
        if self.__session is not None:
            self.__session.add(obj)

    def save(self):
        """Commits all changes to the current database session"""
        if self.__session is not None:
            self.__session.commit()

    def delete(self, obj=None):
        """Deletes an object from the current database session"""
        if obj is None:
            return
        if self.__session is not None:
            self.__session.delete(obj)

    def close(self):
        """Closes the current database session"""
        if self.__session is not None:
            """Call remove() method on the private session attribute"""
            self.__session.remove()
