from nose.tools import *
from mongoalchemy.fields import *
from test.util import get_session
from mongoalchemy.document import Document


class V(Document):
    i = IntField()
    s = StringField()


def setup():
    s = get_session()
    s.clear_collection(V)

    for n in xrange(5):
        obj = V(i=n, s=chr(65+n))
        s.insert(obj)


# TODO: Test DocumentField retrieval, etc.
def test_basic():
    s = get_session()
    i = 0
    for t in s.query(V).fields(V.i, values_only=True).all():
        assert t[0] == i
        i += 1
    i = 0
    for t in s.query(V).fields(V.s, values_only=True).all():
        assert t[0] == chr(65+i)
        i += 1


def test_clone_basic():
    s = get_session()
    query = s.query(V).fields(V.i, values_only=True)
    query = query.clone()

    i = 0
    for t in query.all():
        assert t[0] == i
        i += 1


def test_clone_modify_fields():
    s = get_session()
    q = s.query(V).fields(V.i, values_only=True)
    q2 = q.clone()

    q2.fields(V.s)

    i = 0
    for t in q:
        assert len(t) == 1
        assert t[0] == i
        i += 1

    i = 0
    for t in q2:
        assert len(t) == 2
        assert t[0] == i
        assert t[1] == chr(65+i)
        i += 1


def test_getitem():
    s = get_session()
    q = s.query(V).fields(V.i, values_only=True)

    assert q[0] == (0,)


def test_one():
    s = get_session()
    q = s.query(V).fields(V.i, values_only=True).filter(V.i == 0)

    assert q.one() == (0,)


def test_named():
    s = get_session()
    q = s.query(V).fields(V.i, values_only=True).filter(V.i == 0).one()

    assert q.i == 0

