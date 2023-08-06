from __future__ import absolute_import

import struct
from .fields import StructField

class StructMeta(type):
    def __new__(cls, name, bases, attrs):
        fields = []
        for attr_name, attr_value in list(attrs.items()):
            if not isinstance(attr_value, StructField):
                continue
            attr_value.name = attr_name
            fields.append(attr_value)
            del attrs[attr_name]

        if len(fields) > 0:
            fields.sort(key=lambda field: field._field_order)
            format = "!" + "".join(f.format for f in fields)
            attrs["fields"] = fields
            attrs["struct"] = struct.Struct(format)

        return super(StructMeta, cls).__new__(cls, name, bases, attrs)

class StructBase(StructMeta("StructBase", (object, ), {})):
    #__metaclass__ = StructMeta

    def __init__(self, raw_data):
        data = self.struct.unpack_from(raw_data)
        for field, value in zip(self.fields, data):
            setattr(self, field.name, field.handle(value))

    def __repr__(self):
        return "<{0} {1}>".format(
            self.__class__.__name__,
            ", ".join("{0}: {1!r}".format(field.name, getattr(self, field.name, None))
                      for field in self.fields)
        )
