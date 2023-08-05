import ming
from ming.datastore import DataStore
from ming import Session
from ming import schema as s
from ming.orm import ThreadLocalORMSession, FieldProperty, Mapper
from ming.orm.declarative import MappedClass

mainsession = Session()
DBSession = ThreadLocalORMSession(mainsession)

database_setup = False
bind = None

def setup_database():
    global bind, database_setup
    if not database_setup:
        bind = DataStore('mim:///', database='test')
        mainsession.bind = bind
        ming.orm.Mapper.compile_all()
        database_setup = True

def clear_database():
    global engine, database_setup
    if not database_setup:
        setup_database()

class Thing(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'thing'

    _id = FieldProperty(s.ObjectId)
    name = FieldProperty(s.String)
