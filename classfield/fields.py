from django.db import models
from django.db.models import SubfieldBase
from django.utils.translation import ugettext_lazy as _


class ClassField(models.Field):

    description = _('Class Field')

    __metaclass__ = SubfieldBase

    def __init__(self, *args, **kwargs):
        if 'choices' not in kwargs:
            kwargs['editable'] = False

        kwargs.setdefault('max_length', 256)
        super(ClassField, self).__init__(*args, **kwargs)


    def get_prep_value(self, value):
        return "%s.%s" % (value.__module__, value.__name__)


    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        if value is None or value == '':
            return None

        parts = value.split( "." )
        imported = __import__('.'.join(parts[:-1]), globals(), locals(), [parts[-1]], 0)
        return getattr(imported, parts[-1])


    def get_db_prep_lookup(self, lookup_type, value):
        # We only handle 'exact' and 'in'. All others are errors.
        if lookup_type == 'exact':
            return [self.get_db_prep_save(value)]
        elif lookup_type == 'in':
            return [self.get_db_prep_save(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)


