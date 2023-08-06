from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column, asc, desc
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from sqlalchemy.orm.interfaces import MapperExtension
from datetime import datetime

from BeautifulSoup import BeautifulSoup
from core import DeclarativeBase, DBSession
import re
from ConfigParser import ConfigParser
from StringIO import StringIO

class Attribute(DeclarativeBase):
    __tablename__ = 'acr_cms_attributes'

    uid = Column(Integer, primary_key=True)
    name = Column(Unicode(32), nullable=False, index=True)
    value = Column(Binary(4*1024*1024))
   
    slice_uid = Column(Integer, ForeignKey('acr_cms_slice.uid'))
    slice = relation('Slice', backref=backref('attributes', cascade='all, delete-orphan'))
    
    page_uid = Column(Integer, ForeignKey('acr_cms_page.uid'))
    page = relation('Page', backref=backref('attributes', cascade='all, delete-orphan'))
