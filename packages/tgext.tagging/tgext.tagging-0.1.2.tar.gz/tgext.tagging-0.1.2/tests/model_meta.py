from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import Integer

maker = sessionmaker(autoflush=True, autocommit=False)
DBSession = scoped_session(maker)
DeclarativeBase = declarative_base()
metadata = DeclarativeBase.metadata 

class User(DeclarativeBase):
    __tablename__ = 'users'

    uid = Column(Integer, autoincrement=True, primary_key=True)

class FakeObject(DeclarativeBase):
    __tablename__ = 'object'

    uid = Column(Integer, autoincrement=True, primary_key=True)