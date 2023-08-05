from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

maker = sessionmaker(autoflush=True, autocommit=False)
DBSession = scoped_session(maker)
DeclarativeBase = declarative_base()
metadata = DeclarativeBase.metadata

database_setup=False
engine = None

def setup_database():
    global engine, database_setup
    if not database_setup:
        engine = create_engine('sqlite:///:memory:', strategy="threadlocal")
        DBSession.configure(bind=engine)
        database_setup = True

def clear_database():
    global engine, database_setup
    if not database_setup:
        setup_database()

    DBSession.rollback()
    DeclarativeBase.metadata.drop_all(engine)
    DeclarativeBase.metadata.create_all(engine)


class Thing(DeclarativeBase):
    __tablename__ = 'thing'

    uid = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Unicode(16), unique=True)

