from sqlalchemy import create_engine
from model_meta import DBSession, metadata, DeclarativeBase, User
from tgext.tagging.model.setup import setup_model

engine = create_engine('sqlite:///:memory:')
setup_model(dict(DeclarativeBase=DeclarativeBase, metadata=metadata, DBSession=DBSession, User=User))

def setup():
    print 'SETTING UP MODEL'
    DBSession.configure(bind=engine)
    metadata.create_all(engine)

def teardown():
    print 'TEARING DOWN MODEL'
    metadata.drop_all(engine)

