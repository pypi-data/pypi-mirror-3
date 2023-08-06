import unittest

from destruct import StructBase
import destruct.fields as f
import datetime

class MyStruct(StructBase):
    timestamp = f.TimestampField()
    value8 = f.U8Field()
    value16 = f.U16Field()
    value32 = f.U32Field()

class TestSimpleStruct(unittest.TestCase):
    def test_parse(self):
        epoch = datetime.datetime.utcfromtimestamp(0)
        data = MyStruct(b"\0\0\0\0\x80\xFF\xFF\0\0\0\xFF")
        self.assertEqual(data.timestamp, epoch)
        self.assertEqual(data.value8, 128)
        self.assertEqual(data.value16, 65535)
        self.assertEqual(data.value32, 255)

    def test_repr(self):
        data = MyStruct(b"\0\0\0\0\x80\xFF\xFF\0\0\0\xFF")
        expected_repr = \
            "<MyStruct" \
            " timestamp: datetime.datetime(1970, 1, 1, 0, 0)," \
            " value8: 128, value16: 65535, value32: 255>"
        self.assertEqual(repr(data), expected_repr)

if __name__ == "__main__":
    unittest.main()
