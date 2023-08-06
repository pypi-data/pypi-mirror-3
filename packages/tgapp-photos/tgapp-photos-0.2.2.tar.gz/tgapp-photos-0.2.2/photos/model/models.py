from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime
from sqlalchemy.orm import backref, relation

from photos.model import DeclarativeBase
from tgext.pluggable import app_model, primary_key

from tgext.datahelpers.fields import Attachment, AttachedImage

class Gallery(DeclarativeBase):
    __tablename__ = 'photos_gallery'

    uid = Column(Integer, nullable=False, primary_key=True)
    name = Column(Unicode(100), nullable=False)

class Photo(DeclarativeBase):
    __tablename__ = 'photos_photo'

    uid = Column(Integer, nullable=False, primary_key=True)
    name = Column(Unicode(100), nullable=False)
    description = Column(Unicode(2048), nullable=False)
    image = Column(Attachment(AttachedImage))

    author_id = Column(Integer, ForeignKey(primary_key(app_model.User)))
    author = relation(app_model.User, backref=backref('photos'))

    gallery_id = Column(Integer, ForeignKey(Gallery.uid))
    gallery = relation(Gallery, backref=backref('photos', cascade='all, delete-orphan'))
