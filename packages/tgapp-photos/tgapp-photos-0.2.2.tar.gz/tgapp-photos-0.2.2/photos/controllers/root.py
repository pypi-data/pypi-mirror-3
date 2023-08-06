# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import TGController
from tg import expose, flash, require, url, lurl, request, redirect, validate
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg.decorators import cached_property

from photos import model
from photos.model import DBSession, Gallery

from repoze.what import predicates
from tgext.crud import EasyCrudRestController

try:
    from tw2.forms import FileField
    from formencode.validators import FieldStorageUploadConverter
except ImportError:
    from tw.forms import FileField
    from tw.forms.validators import FieldStorageUploadConverter

from tgext.datahelpers.validators import SQLAEntityConverter
from tgext.pluggable import plug_url, primary_key, app_model
from webhelpers import html

class PhotosController(EasyCrudRestController):
    allow_only = predicates.in_group('photos')
    title = "Manage Photos"
    model = model.Photo
    keep_params = ['gallery']

    __form_options__ = {
        '__hide_fields__' : ['uid', 'author', 'gallery'],
        '__field_widget_types__' : {'image':FileField},
        '__field_validator_types__' : {'image':FieldStorageUploadConverter},
        '__field_widget_args__' : {'author':{'default':lambda:getattr(request.identity['user'],
                                                                      primary_key(app_model.User).key)}}
    }

    __table_options__ = {
        '__omit_fields__' : ['uid', 'author_id', 'gallery_id', 'gallery'],
        '__xml_fields__' : ['image'],
        'image': lambda filler,row: html.literal(row.image and '<img src="%s"/>' % row.image.thumb_url or '<span>no image</span>')
    }

    @property
    def mount_point(self):
        return plug_url('photos', '/manage/photos')

class GalleriesController(EasyCrudRestController):
    allow_only = predicates.in_group('photos')
    title = "Manage Galleries"
    model = model.Gallery

    __form_options__ = {
        '__hide_fields__' : ['uid'],
        '__omit_fields__' : ['photos']
    }

    @property
    def mount_point(self):
        return plug_url('photos', '/manage/galleries')

class ManagementController(TGController):
    @cached_property
    def galleries(self):
        return GalleriesController(DBSession.wrapped_session)

    @cached_property
    def photos(self):
        return PhotosController(DBSession.wrapped_session)

class RootController(TGController):
    manage = ManagementController()

    @expose('genshi:photos.templates.index')
    def index(self, *args, **kw):
        galleries = DBSession.query(Gallery).order_by(Gallery.uid.desc()).all()
        return dict(galleries=galleries)

    @expose('genshi:photos.templates.gallery')
    @validate(dict(gallery=SQLAEntityConverter(Gallery)), error_handler=index)
    def gallery(self, gallery):
        return dict(gallery=gallery)
