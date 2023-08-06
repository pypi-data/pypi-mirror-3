import tg
from formencode import Invalid, FancyValidator

try:
    import sqlalchemy

    class SQLAEntityConverter(FancyValidator):
        def __init__(self, klass, session=None):
            super(FancyValidator, self).__init__()
            self.klass = klass
            self.session = session

        def _to_python(self, value, state):
            if self.session is None:
                self.session = tg.config['DBSession']
            return self.session.query(self.klass).get(value)

        def validate_python(self, value, state):
            if not value:
                raise Invalid('object not found', value, state)

except ImportError:
    pass


try:
    import ming
    from bson import ObjectId

    class MingEntityConverter(FancyValidator):
        def __init__(self, klass):
            super(FancyValidator, self).__init__()
            self.klass = klass

        def _to_python(self, value, state):
            try:
                obj_id = ObjectId(value)
            except:
                raise Invalid('object not found', value, state)
            
            return self.klass.query.get(_id=obj_id)

        def validate_python(self, value, state):
            if not value:
                raise Invalid('object not found', value, state)

except ImportError:
    pass