import AccessControl
import DateTime
import utilities
from smtplib import SMTP 
import id_config
from Globals import InitializeClass

def _display(x, issue_short_url):
    text = x.get_title + ' (%s, %s)' % (x.get_type, x.state) + ':\n' + issue_short_url + x.id + '\n\n'
    if len(x.render_contents_as_text) > 500:
        text += x.render_contents_as_text[:500] + '[...]\n\n'
    else:
        text += x.render_contents_as_text + '\n\n'
    return text

def _short_due_display(x, issue_short_url):
    text = x.get_title + ' (%s, %s)' % (x.get_type, x.state) + ':\n' + issue_short_url + x.id + '\n' + \
		'Due: ' + str(x.render_due) + '\n\n'
    return text

def make_display(issue_short_url):
    # Whopty doo
    return lambda x, issue_short_url=issue_short_url: _display(x, issue_short_url)

def make_short_due_display(issue_short_url):
    # Whopty doo
    return lambda x, issue_short_url=issue_short_url: _short_due_display(x, issue_short_url)

class issue_dealer_notifications:

    security = AccessControl.ClassSecurityInfo()

    security.declarePublic('check_notifications')
    def check_notifications(self, raise_error=1):
        """Checks to see if any notifications are to be made."""
        if not self.has_absolute_url():
            return
        current_check = DateTime.DateTime()
        issue_short_url = self.get_issue_dealer().get_custom_absolute_url() + '/r?i='
        display = make_display(issue_short_url)
        short_due_display = make_short_due_display(issue_short_url)
        if self.last_notification_check == None:
            self.last_notification_check = current_check
        new_in_session, changed_in_session, new_owned, changed_owned, past_due = [], [], [], [], []
        changed_session, new_session = 0, 0
        for preferences in self.catalog_search(meta_type='Preferences'):
            try:
                if not preferences.email.strip():
                    continue
                email = "Subject: Tracked Issues\nFrom: 'Issue Dealer Notifier' <%s>\nTo: <%s>\n\n" % (preferences.email, preferences.email)
                if preferences.notify_owned_new:
                    new_owned = self.catalog_search(owners=preferences.owner_, meta_type='Issue',
			created={'query':self.last_notification_check, 'range':'min'})
                if preferences.notify_owned_changed:
                    if preferences.notify_owned_new:
                        created={'query':self.last_notification_check, 'range':'max'}
                    else:
                        created=None
                    changed_owned = self.catalog_search(owners=preferences.owner_, meta_type='Issue',
			modified={'query':self.last_notification_check, 'range':'min'}, created=created)
                if preferences.notify_past_due:
                    past_due = self.catalog_search(owners=preferences.owner_, meta_type='Issue',
			due={'query':(DateTime.DateTime('1970-01-01'), current_check), 'range':'min:max'},
			is_action_issue=True, state='open')
                if past_due:
                    email += 'Issues past due date:\n\n'
                    email += ''.join(map(short_due_display, past_due)) + '\n'
                if new_owned:
                    email += 'New issues owned:\n\n'
                    email += ''.join(map(display, new_owned)) + '\n'
                if changed_owned:
                    email += 'Changed issues owned:\n\n'
                    email += ''.join(map(display, changed_owned)) + '\n'
                if preferences.notify_session_new:
                    new_session = self.catalog_search(meta_type='Issue',
			created={'query':self.last_notification_check, 'range':'min'},
			get_parent_ids=self.get_session(preferences=preferences).marks)
                    new_owned_ids = map(lambda x: x.id, new_owned)
                    new_session = filter(lambda x: not x.id in new_owned_ids, new_session)
                if preferences.notify_session_changed:
                    if preferences.notify_session_new:
                        created={'query':self.last_notification_check, 'range':'max'}
                    else:
                        created=None
                    changed_session = self.catalog_search(meta_type='Issue',
			modified={'query':self.last_notification_check, 'range':'min'},
			get_parent_ids=self.get_session(preferences=preferences).marks,
			created=created)
                    changed_owned_ids = map(lambda x: x.id, changed_owned)
                    changed_session = filter(lambda x: not x.id in changed_owned_ids, changed_session)
                if new_session:
                    email += 'New issues in session:\n\n'
                    email += ''.join(map(display, new_session)) + '\n'
                if changed_session:
                    email += 'Changed issues in session:\n\n'
                    email += ''.join(map(display, changed_session)) + '\n'                
                if new_owned or changed_owned or new_session or changed_session or past_due:
                    try:
                        SMTP(id_config.smtp).sendmail(preferences.email, [preferences.email], email)
                    except:
                        if raise_error: raise
                        utilities.dump_error_log()
            except:
                if raise_error: raise
                else: utilities.dump_error_log()
        self.last_notification_check = current_check

InitializeClass(issue_dealer_notifications)