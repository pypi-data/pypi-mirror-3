from nose.tools import *
from mongoalchemy.fields import AutoIncrementField
from test.util import known_failure, get_session
from mongoalchemy.document import Document, Index, DocumentField, \
        MissingValueException, DocumentException, DictDoc, \
        document_type_registry


def test_definition():
    # Make sure this doesn't raise any errors
    class DocDef(Document):
        a = AutoIncrementField()

    d = DocDef()


def test_save():
    class Doc(Document):
        a = AutoIncrementField()

    d = Doc()
    s = get_session()
    s.insert(d)


def test_first_increment():
    class DocOne(Document):
        a = AutoIncrementField()

    d = DocOne()
    s = get_session()
    s.insert(d)

    assert d.a == 1


def test_no_increment():
    class Doc(Document):
        a = AutoIncrementField()

    d = Doc()
    d.a = -1
    s = get_session()
    s.insert(d)

    assert d.a == -1


def test_increment_induction():
    class DocInc(Document):
        a = AutoIncrementField()

    d = DocInc()
    s = get_session()
    s.insert(d)

    assert d.a == 1

    d2 = DocInc()
    s.insert(d2)

    assert d2.a == 2

    d3 = DocInc()
    s.insert(d3)

    assert d3.a == 3


def test_multi_field():
    class DocMulti(Document):
        a = AutoIncrementField()
        b = AutoIncrementField()

    d = DocMulti()
    s = get_session()
    s.insert(d)
    assert d.a == 1 and d.b == 1

    d = DocMulti()
    s.insert(d)
    assert d.a == 2 and d.b == 2


def test_with_db_field_any():
    class DocDBFieldAny(Document):
        a = AutoIncrementField(db_field='any')

    d = DocDBFieldAny()
    s = get_session()
    s.insert(d)
    assert d.a == 1


def test_with_db_field_id():
    class DocDBFieldId(Document):
        a = AutoIncrementField(db_field='_id')

    d = DocDBFieldId()
    s = get_session()
    s.insert(d)
    assert d.a == 1
    assert d.mongo_id == 1

