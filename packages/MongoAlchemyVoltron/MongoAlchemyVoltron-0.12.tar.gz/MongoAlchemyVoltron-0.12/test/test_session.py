from nose.tools import *
from mongoalchemy.session import Session
from mongoalchemy.document import Document, Index, DocumentField
from mongoalchemy.fields import *
from test.util import known_failure, DB_NAME
from pymongo.errors import DuplicateKeyError

class T(Document):
    i = IntField()
    l = ListField(IntField(), required=False, on_update='$pushAll')

class TUnique(Document):
    i = IntField()
    main_index = Index().ascending('i').unique()


def test_session():
    s = Session.connect(DB_NAME)
    s.clear_collection(T)
    s.insert(T(i=1))
    s.clear()
    s.end()

def test_context_manater():
    with Session.connect(DB_NAME) as s:
        s.clear_collection(T)
        t = T(i=5)

def test_safe():
    s = Session.connect(DB_NAME, safe=True)
    assert s.safe == True
    s = Session.connect(DB_NAME, safe=False)
    assert s.safe == False

def test_safe_with_error():
    s = Session.connect(DB_NAME)
    s.clear_collection(TUnique)
    s.insert(TUnique(i=1))
    try:
        s.insert(TUnique(i=1), safe=True)
        assert False, 'No error raised on safe insert for second unique item'
    except DuplicateKeyError:
        assert len(s.queue) == 0


def test_update():
    s = Session.connect(DB_NAME)
    s.clear_collection(T)
    t = T(i=6)
    s.insert(t)
    assert s.query(T).one().i == 6

    t.i = 7
    s.update(t)
    assert s.query(T).one().i == 7


def test_update_change_ops():
    s = Session.connect(DB_NAME)
    s.clear_collection(T)
    t = T(i=6, l=[8])
    s.insert(t)
    assert s.query(T).one().i == 6

    t.i = 7
    t.l = [8]
    s.update(t, update_ops={T.l:'$pullAll'}, i='$inc')
    t = s.query(T).one()
    assert t.i == 13, t.i
    assert t.l == [], t.l

def test_update_push():
    s = Session.connect(DB_NAME)
    s.clear_collection(T)
    # Create object
    t = T(i=6, l=[3])
    s.insert(t)
    t = s.query(T).one()
    assert t.i == 6 and t.l == [3]

    t = s.query(T).fields(T.i).one()
    t.i = 7
    t.l = [4]
    s.update(t, id_expression=T.i == 6)

    t = s.query(T).one()
    assert s.query(T).one().i == 7 and t.l == [3, 4]

