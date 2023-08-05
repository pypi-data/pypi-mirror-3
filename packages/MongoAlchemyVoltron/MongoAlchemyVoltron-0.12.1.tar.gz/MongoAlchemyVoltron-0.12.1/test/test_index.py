from nose.tools import *
from mongoalchemy.document import Document, Index, DocumentField
from mongoalchemy.fields import *
from test.util import known_failure, get_session

class TestDoc(Document):

    int1 = IntField()
    str1 = StringField()
    str2 = StringField()
    str3 = StringField()

    index_1 = Index().ascending('int1').descending('str3')
    index_2 = Index().descending('str3')
    index_3 = Index().descending('str2').unique()
    index_4 = Index().descending('str1').unique(drop_dups=True)

def test_indexes():
    s = get_session()
    s.clear_collection(TestDoc)
    t = TestDoc(int1=1, str1='a', str2='b', str3='c')
    s.insert(t)
    expected = (
            ('_id_', {'key':[('_id', 1)]}),
            ('int1_1_str3_-1', {'key':[('int1', 1), ('str3', -1)], 'dropDups':False}),
            ('str3_-1', {'key':[('str3', -1)], 'dropDups':False}),
            ('str2_-1', {'key':[('str2', -1)], 'unique':True, 'dropDups':False}),
            ('str1_-1', {'key':[('str1', -1)], 'unique':True, 'dropDups':True})
            )
    got = s.get_indexes(TestDoc)
    for idx, d in expected:
        assert idx in got
        for k, v in d.iteritems():
            assert got[idx][k] == d[k]

@known_failure
@raises(Exception)
def no_field_index_test():
    class TestDoc2(TestDoc):
        index_1 = Index().ascending('noexists')
    s.get_session()
    s.clear_collection(TestDoc)
    s.insert(t)

