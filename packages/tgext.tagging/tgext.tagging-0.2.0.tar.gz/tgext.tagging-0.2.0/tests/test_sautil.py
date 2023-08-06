from nose.tools import raises
from sqlalchemy import Table, ForeignKey, Column, and_, create_engine
from sqlalchemy.types import Unicode, Integer
from model_meta import DeclarativeBase

from tgext.tagging.model.sautils import get_primary_key

class TestModel(DeclarativeBase):
    __tablename__ = 'test_model'

    pfield = Column(Integer, autoincrement=True, primary_key=True)

class NonIntegerPrimaryKey(DeclarativeBase):
    __tablename__ = 'test_model_with_wrong_key'

    name = Column(Unicode(127), primary_key=True)
    
class TestSAUtils(object):
    def test_primary_key(self):
        assert get_primary_key(TestModel) == 'pfield'

    @raises(LookupError)
    def test_model_missing_key(self):
        print get_primary_key(NonIntegerPrimaryKey)