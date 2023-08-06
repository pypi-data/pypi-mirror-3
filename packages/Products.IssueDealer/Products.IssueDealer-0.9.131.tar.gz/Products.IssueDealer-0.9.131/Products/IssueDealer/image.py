import Globals
from OFS import Image, Folder
import AccessControl
from Products import ZCatalog
import base, mixins, session_manager, permissions

def add_image(self, id='', file='', content_type='', precondition='', title=''):
    """Adds an image."""
    id=str(id)
    title=str(title)
    content_type=str(content_type)
    precondition=str(precondition)
    id, title = Image.cookId(id, title, file)
    self=self.this()
    # First, we create the image without data:
    self._setObject(id, image(id,title,'',content_type, precondition))
    # Now we "upload" the data.  By doing this in two steps, we
    # can use a database trick to make the upload more efficient.
    if file:
        self._getOb(id).manage_upload(file)
    if content_type:
        self._getOb(id).content_type=content_type
    self._getOb(id).version = self.get_issue_dealer().filesystem_version
    return id

class image(mixins.catalog,
            ZCatalog.CatalogPathAwareness.CatalogAware,
	    Image.Image,
	    Folder.Folder,
	    base.base,
	    session_manager.session_manager):
    """Simple image class."""

    security = AccessControl.ClassSecurityInfo()
    security.declareProtected(permissions.view_issue_dealer, 'index_html', '')

    meta_type = 'Image'
    version = (0,9,70)

    def __init__(self, *arguments, **keywords):
        Image.Image.__init__.im_func(self, *arguments, **keywords)

    def manage_afterAdd(self, item, container):
        Image.Image.manage_afterAdd.im_func(self, item, container)
        image.inheritedAttribute('manage_afterAdd')(self, item, container)

    def manage_afterClone(self, item, container):
        Image.Image.manage_afterClone.im_func(self, item, container)
        image.inheritedAttribute('manage_afterClone')(self, item, container)

    def manage_beforeDelete(self, item, container):
        Image.Image.manage_beforeDelete.im_func(self, item, container)
        image.inheritedAttribute('manage_beforeDelete')(self, item, container)

Globals.InitializeClass(image)




