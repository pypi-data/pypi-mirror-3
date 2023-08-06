from . import db


def init(settings):
    db.init(settings['database'])

