import hashlib
import os.path

from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy


HASHED_PASSWORD_LENGTH = 128
DATA_BASE_NAME = 'sqlite:///' + os.path.join(os.path.dirname(__file__), 'db.sqlite3')

base = declarative_base()
engine = sqlalchemy.create_engine(DATA_BASE_NAME, connect_args={'check_same_thread': False})
base.metadata.bind = engine
session = orm.scoped_session(orm.sessionmaker())(bind=engine)

# after this:
# base == db.Model
# session == db.session
# other db.* values are in sa.*
# ie: old: db.Column(db.Integer,db.ForeignKey('s.id'))
#     new: sa.Column(sa.Integer,sa.ForeignKey('s.id'))
# except relationship, and backref, those are in orm
# ie: orm.relationship, orm.backref
# so to define a simple model


def hash_password(password: str) -> str:
    return hashlib.sha512(password.encode()).hexdigest()


class User(base):
    __tablename__ = 'users'  # <- must declare name for db table
    # id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    username = sqlalchemy.Column(sqlalchemy.String(255), nullable=False, primary_key=True)
    password = sqlalchemy.Column(sqlalchemy.String(HASHED_PASSWORD_LENGTH), nullable=False)

    @classmethod
    def add_user(cls, username: str, password: str):
        user = cls(username=username, password=hash_password(password))
        session.add(user)
        session.commit()

    @classmethod
    def find(cls, username: str):
        """
        :param username: the username you want to add.
        :return: the user with this username. If user does not exists return None.
        """
        return session.query(cls).filter_by(username=username).first()

    @classmethod
    def valid_user(cls, username: str, password: str):
        user = cls.find(username)
        if user is None:
            return False

        return hash_password(password) == user.password

    def __repr__(self):
        return f'<User {self.username}>'


base.metadata.create_all(engine)
