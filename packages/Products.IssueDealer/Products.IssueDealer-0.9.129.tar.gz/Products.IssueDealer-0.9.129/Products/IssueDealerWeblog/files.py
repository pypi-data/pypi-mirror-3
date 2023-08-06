from Globals import Persistent
import OFS
import Acquisition
import AccessControl
from DateTime import DateTime

class files(
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager):
    """File handler, for proxied files."""

    security = AccessControl.ClassSecurityInfo()

    def __init__(self, id):
        self.id = id

    def __bobo_traverse__(self, REQUEST, id):
        id, filename = REQUEST['PATH_INFO'].split('/')[-2:]
        assert self.get_weblog_publisher().been_published(id)
        issue = self.get_object(id)
        file = getattr(issue.aq_base, filename)
        return file.index_html(REQUEST, REQUEST.RESPONSE)
