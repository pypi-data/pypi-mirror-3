from Globals import Persistent, InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
import Acquisition
import AccessControl
import base
import session
import mixins
import permissions

def manage_addSessionFolder(self, id=None, REQUEST=None):
    """Add a Session Folder."""
    if id is None:
        id = self.get_unique_id()
    session_folder_ = session_folder(id)
    self._setObject(id, session_folder_)
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return session_folder_

class session_folder(
    mixins.catalog,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base
    ): 
    """Session folder.

    Used to group sessions.
    """

    title = 'No title'
    meta_type = 'Session Folder'
    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(permissions.view_issue_dealer, 'index_html', 'get_title')
    index_html = PageTemplateFile('skins/issue_dealer/issue_dealer_session_folder_index.pt', globals())
    security.declareProtected(permissions.view_issue_dealer, 'manage_addSession')
    manage_addSession = session.manage_addSession

    all_meta_types = [
        {'visibility': 'Global',
         'interfaces': [],
         'action': 'manage_add_issue',
         'permission': 'Add sessions',
         'name': 'Session',
         'product': 'Issue Dealer',
         'instance': ''}
    ]

    def __init__(self, id, title=''):
        self.id = id
        self.title = title

InitializeClass(session_folder)
