from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Unicode
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey

from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class Shard(Base):
    """A piece of a web page."""
    # XXX where to put cache duration?
    __tablename__ = 'shard'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    url = Column(Unicode(512))
    selector = Column(Unicode(255)) # a jQuery selector
    width = Column(Integer)
    height = Column(Integer)
    triggers = Column(Integer, nullable=False, default=0)

class Slideshow(Base):
    __tablename__ = 'slideshow'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255), unique=True)
    
class Slide(Base):
    __tablename__ = 'slide'
    id = Column(Integer, primary_key=True)
    order = Column(Integer)
    duration = Column(Integer)
    shard_id = Column(Integer, ForeignKey(Shard.id))
    shard = relationship(Shard, backref='slides')
    slideshow_id = Column(Integer, ForeignKey(Slideshow.id))
    slideshow = relationship(Slideshow, backref=backref('slides', order_by='Slide.order'))
