========
destruct
========

Destruct is a tiny library to declaratively define data structures
and parse them to Python objects.

The library is not mature by any means. Things may break, and API may
significantly change in future.

.. image:: https://secure.travis-ci.org/drdaeman/destruct.png?branch=master

Example
-------

Data structures are declared in a manner somehow similar to Django models::

    from destruct import StructBase
    import destruct.fields as f

    class MyStruct(StructBase):
        timestamp = f.TimestampField()
        value = f.U32Field()

Then, parsing is just creating object::

    data = MyStruct(b"\0\0\0\0\0\0\0\xFF")
    assert data.timestamp == datetime.datetime.utcfromtimestamp(0)
    assert data.value == 255

Copyright
---------

Copyright (c) 2012, Aleksey Zhukov. Distributed under MIT (Expat) license.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

The software is provided **"as is"**, *without warranty of any kind*, express or
implied, including but not limited to the warranties of merchantability, fitness
for a particular purpose and noninfringement. *In no event* shall the authors or
copyright holders be liable for any claim, damages or other liability,
whether in an action of contract, tort or otherwise, arising from, out of
or in connection with the software or the use or other dealings in the software.
