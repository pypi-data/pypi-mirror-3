from photos.model import DBSession, Gallery
from tg import expose

@expose('genshi:photos.templates.gallery_partial')
def gallery(gallery=None):
    if gallery is None:
        gallery = DBSession.query(Gallery).first()
    return dict(gallery=gallery)