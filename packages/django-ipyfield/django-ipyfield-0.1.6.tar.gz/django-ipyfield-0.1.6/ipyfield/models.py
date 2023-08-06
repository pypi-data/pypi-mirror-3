from django.conf import settings
if 'south' in settings.INSTALLED_APPS:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^ipyfield\.models\.IPyField"])


from django.db import models
from IPy import IP


class IPyField(models.Field):
    """
    Handles conversion between int db column and IP instance.
    """
    
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if not value: 
            return None
        elif isinstance(value, IP):
            return value
        else:
            return IP(value)

    def get_prep_value(self, value):
        value = self.to_python(value)
        if not value:
            return None
        return str(value.int())

    def to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return str(self.get_db_prep_value(value))

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'in':
            if isinstance(value, str):
                value = IP(value)
            return [self.get_prep_value(v) for v in value]
        elif lookup_type in ['exact', 'lt', 'lte', 'gt', 'gte']:
            return self.get_prep_value(value)
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)

    def db_type(self, connection):
        return 'varchar(39)'

    def get_internal_type(self):
        return 'CharField'

