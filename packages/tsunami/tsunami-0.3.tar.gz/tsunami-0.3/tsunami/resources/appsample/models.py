#coding: utf-8
from __future__ import unicode_literals
import time
import uuid
import datetime

import sqlalchemy
from sqlalchemy import MetaData, Table, Column, Index, Integer, BigInteger, String, ForeignKey, Text, DateTime, Boolean, Enum, Float, Numeric, PickleType, Date
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.schema import Sequence, Index
from sqlalchemy.orm import relationship, backref, column_property, deferred
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.interfaces import MapperExtension
from sqlalchemy.ext.declarative import declarative_base

from werkzeug import generate_password_hash, check_password_hash




metadata = MetaData()
Base = declarative_base(metadata=metadata)



class User(Base):
    '''User'''
    __tablename__ = 'user'

    id          = Column(Integer, doc='ID', primary_key=True, index=True)
    account     = Column(String(32),  doc='帐号', unique=True, index=True)
    password    = Column(String(128), doc='密码', nullable=False)

    name        = Column(String(32),  doc='名称')
    phone       = Column(String(128),  doc='电话')

    create_ip   = Column(String(128), doc='注册IP地址')
    create_time = Column(DateTime,   doc='创建时间', default=datetime.datetime.now)

    def validate_password(self, raw_password):
        return check_password_hash(self.password, raw_password)

    def set_password(self, raw_password):
        self.password = generate_password_hash(raw_password)

