from Globals import InitializeClass
import AccessControl
from session import manage_addSession
import permissions

class session_manager:
    """Mixin class to handle sessions."""

    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(permissions.view_issue_dealer, 'handle_session')
    def handle_session(self):
        """Does session related things."""
        preferences = self.get_user_preferences()
        if not preferences.issue_dealer_session:
            sessions = self.get_issue_dealer().sessions
            if not sessions.objectIds():
                # Is no sessions exist, add one
                manage_addSession(sessions)
            # Find a session to work in
            session = self.catalog_search(users=self.get_user().get_id())
            if len(session):
                session = session[0]
            else:
                session = sessions.objectValues()[0]
                session.add_user(self.get_user().get_id())
            preferences.issue_dealer_session = session.id

    security.declareProtected(permissions.view_issue_dealer, 'get_session')
    def get_session(self, preferences=None):
        """Returns the session the user is currently working in."""
        id = self.get_issue_dealer()
        sessions = id.sessions
        preferences = preferences or self.get_user_preferences()
        return sessions[preferences.issue_dealer_session]

InitializeClass(session_manager)
