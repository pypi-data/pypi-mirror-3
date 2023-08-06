from __future__ import absolute_import

from datetime import datetime

class StructField(object):
    _counter = 0

    def __init__(self, format, conversion=None):
        StructField._counter += 1
        self._field_order = StructField._counter
        self.name = None
        self.format = format
        self.conversion = conversion

    def handle(self, value):
        if self.conversion is not None:
            return self.conversion(value)
        return value

    def __repr__(self): # pragma: no cover
        return "<{cls} {self.name}({self.format})>".format(
            cls=self.__class__.__name__, self=self
        )

class U8Field(StructField):
    def __init__(self):
        super(U8Field, self).__init__("B")

class U16Field(StructField):
    def __init__(self):
        super(U16Field, self).__init__("H")

class U32Field(StructField):
    def __init__(self):
        super(U32Field, self).__init__("L")

class TimestampField(StructField):
    def __init__(self):
        super(TimestampField, self).__init__("L", conversion=datetime.utcfromtimestamp)
