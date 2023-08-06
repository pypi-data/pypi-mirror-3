import AccessControl
import permissions as id_permissions
from Globals import InitializeClass

class base_browse:

    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(id_permissions.view_issue_dealer, 'browse_stop')
    def browse_stop(self):
        """Stops browse mode."""
        del self.REQUEST.SESSION['browse']
        self.REQUEST.RESPONSE.redirect(self.absolute_url())

    security.declareProtected(id_permissions.view_issue_dealer, 'render_browse_previous')
    def render_browse_previous(self):
        """Renders a link to the previous object, if any."""
        if self.REQUEST.SESSION['browse_index'] - 1 > -1:
            return """<a href="%s?previous=" class="button">&lt;&lt; Previous""" % \
              (self.get_object(self.REQUEST.SESSION['browse'][
		self.REQUEST.SESSION['browse_index'] - 1]).absolute_url)
        else: return """<span class="disabled">&lt;&lt; Previous</span>"""

    security.declareProtected(id_permissions.view_issue_dealer, 'render_browse_next')
    def render_browse_next(self):
        """Renders a link to the next object, if any."""
        try:
            return """<a href="%s?next=" class="button">Next &gt;&gt;""" % \
              (self.get_object(self.REQUEST.SESSION['browse'][
		self.REQUEST.SESSION['browse_index'] + 1]).absolute_url)
        except IndexError:
            return """<span class="disabled">Next &gt;&gt;</span>"""

    security.declareProtected(id_permissions.view_issue_dealer, 'handle_browsing')
    def handle_browsing(self):
        """Handles browsing."""
        if self.REQUEST.has_key('previous'):
            self.REQUEST.SESSION['browse_index'] -= 1
        if self.REQUEST.has_key('next'):
            self.REQUEST.SESSION['browse_index'] += 1

    security.declareProtected(id_permissions.view_issue_dealer, 'browse')
    def browse(self):
        """Does some tricks so we can go browsing."""
        results = self.get_search_results()
        self.REQUEST.SESSION.set('browse', map(lambda x: x.id, results))
        self.REQUEST.SESSION.set('browse_start', self.absolute_url())
        self.REQUEST.SESSION.set('browse_index', 0)
        self.REQUEST.RESPONSE.redirect(results[0].absolute_url)

InitializeClass(base_browse)