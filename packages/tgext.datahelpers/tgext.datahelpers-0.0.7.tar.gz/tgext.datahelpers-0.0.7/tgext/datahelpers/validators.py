import tg
from formencode import Invalid, FancyValidator
from tgext.datahelpers.utils import object_primary_key

try:
    import sqlalchemy

    class SQLAEntityConverter(FancyValidator):
        def __init__(self, klass, session=None, slugified=False):
            super(FancyValidator, self).__init__(not_empty=True)
            self.klass = klass
            self.session = session
            self.slugified = slugified

        def _to_python(self, value, state):
            if self.session is None:
                self.session = tg.config['DBSession']

            if self.slugified:
                try:
                    value = value.rsplit('-', 1)[-1]
                except:
                    value = value

            return self.session.query(self.klass).get(value)

        def _from_python(self, value, state):
            return getattr(value, object_primary_key(value))

        def validate_python(self, value, state):
            if not value:
                raise Invalid('object not found', value, state)

except ImportError: #pragma: no cover
    pass


try:
    import ming
    from bson import ObjectId

    class MingEntityConverter(FancyValidator):
        def __init__(self, klass, slugified=False):
            super(FancyValidator, self).__init__(not_empty=True)
            self.klass = klass
            self.slugified = slugified

        def _to_python(self, value, state):
            if self.slugified:
                try:
                    value = value.rsplit('-', 1)[-1]
                except:
                    value = value

            try:
                obj_id = ObjectId(value)
            except:
                raise Invalid('object not found', value, state)
            
            return self.klass.query.get(_id=obj_id)

        def _from_python(self, value, state):
            return getattr(value, object_primary_key(value))

        def validate_python(self, value, state):
            if not value:
                raise Invalid('object not found', value, state)

except ImportError: #pragma: no cover
    pass