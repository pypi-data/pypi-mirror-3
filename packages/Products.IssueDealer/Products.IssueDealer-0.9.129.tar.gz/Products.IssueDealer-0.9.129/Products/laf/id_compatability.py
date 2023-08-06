import utilities
from cgi import escape

class id_compatability:

    # ID Stuff

    def delete(self, REQUEST=None):
        """Deletes the object."""
        self.deleted = 1
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])

    def undelete(self, REQUEST=None):
        """Undeletes the object."""
        self.deleted = 0
        if REQUEST:
            REQUEST.RESPONSE.redirect(REQUEST['HTTP_REFERER'])
