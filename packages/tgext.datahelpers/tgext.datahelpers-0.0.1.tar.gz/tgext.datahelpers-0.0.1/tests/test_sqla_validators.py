from formencode import Invalid
from nose.tools import raises
from sqla_base import setup_database, clear_database, DBSession, Thing
from tgext.datahelpers.validators import SQLAEntityConverter

def setup():
    setup_database()

class TestSQLAEntityConverter(object):
    def __init__(self):
        self.validator = SQLAEntityConverter(Thing, DBSession)

    def setup(self):
        clear_database()

    def test_found_entity(self):
        DBSession.add(Thing(uid=2, name=u'Foo'))
        DBSession.add(Thing(uid=1, name=u'Bar'))
        DBSession.flush()

        x = self.validator.to_python(1)
        assert x
        assert x.name == u'Bar'

    @raises(Invalid)
    def test_notfound_entity(self):
        DBSession.add(Thing(uid=1, name=u'Bar'))
        DBSession.flush()

        x = self.validator.to_python(5)

    def test_string_id(self):
        DBSession.add(Thing(uid=1, name=u'Bar'))
        DBSession.flush()

        x = self.validator.to_python('1')
        assert x
        assert x.name == u'Bar'

    @raises(Invalid)
    def test_not_an_id(self):
        DBSession.add(Thing(uid=1, name=u'Bar'))
        DBSession.flush()

        x = self.validator.to_python('asd')