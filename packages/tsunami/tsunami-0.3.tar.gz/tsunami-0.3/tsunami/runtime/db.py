__author__ = 'tsangpo'


import logging
import contextlib
import sqlalchemy.orm



engine = None
sessionmaker = None


def init(database):
    global engine, sessionmaker
    engine = sqlalchemy.create_engine(database)
    sessionmaker = sqlalchemy.orm.sessionmaker(bind=engine)



@contextlib.contextmanager
def session():
    db = sessionmaker()
    try:
        yield db
    except:
        logging.exception('exception in db session')
        raise
    finally:
        db.close()

