from bson import ObjectId
from formencode import Invalid
from nose.tools import raises
from ming_base import setup_database, clear_database, DBSession, Thing
from tgext.datahelpers.validators import MingEntityConverter

def setup():
    setup_database()

class TestMingEntityConverter(object):
    def __init__(self):
        self.validator = MingEntityConverter(Thing)

    def setup(self):
        clear_database()

    def test_found_entity(self):
        t1 = Thing(name=u'Foo')
        t2 = Thing(name=u'Bar')
        DBSession.flush()
        DBSession.close()

        x = self.validator.to_python(t2._id)
        assert x
        assert x.name == u'Bar'

    @raises(Invalid)
    def test_notfound_entity(self):
        t1 = Thing(name=u'Bar')
        DBSession.flush()
        DBSession.close()

        x = self.validator.to_python(ObjectId('000000000000000000000000'))

    def test_string_id(self):
        t1 = Thing(name=u'Bar')
        DBSession.flush()
        DBSession.close()

        x = self.validator.to_python(str(t1._id))
        assert x
        assert x.name == u'Bar'

    @raises(Invalid)
    def test_not_an_id(self):
        t1 = Thing(name=u'Bar')
        DBSession.flush()
        DBSession.close()

        x = self.validator.to_python('asd')