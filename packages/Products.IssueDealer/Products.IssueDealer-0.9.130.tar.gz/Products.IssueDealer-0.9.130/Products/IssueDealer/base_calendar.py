import AccessControl
import permissions as id_permissions
from Globals import InitializeClass, DTMLFile
from DateTime import DateTime
import id_config

class base_calendar:

    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(id_permissions.view_issue_dealer, 'calendar_stripped',
	'calendar_setup_stripped', 'calendar_en', 'calendar_blue')

    calendar_stripped = DTMLFile('skins/issue_dealer/calendar_stripped.js', globals())
    calendar_setup_stripped = DTMLFile('skins/issue_dealer/calendar-setup_stripped.js', globals())
    calendar_en = DTMLFile('skins/issue_dealer/calendar-en.js', globals())
    calendar_blue = DTMLFile('skins/issue_dealer/calendar-blue.css', globals())

    security.declareProtected(id_permissions.view_issue_dealer, 'get_calendar_date_range')
    def get_calendar_date_range(self, offset=0):
        """Gets a date range."""
        start = DateTime((DateTime() + offset).strftime('%Y-%m-%d'))
        dates = []
        for x in range(31):
            dates.append(start + x)
        return dates

    security.declareProtected(id_permissions.view_issue_dealer, 'render_date')
    def render_date(self, date):
        """Renders the date."""
        return date.strftime(id_config.date_format)

    security.declareProtected(id_permissions.view_issue_dealer, 'get_events_for_date')
    def get_events_for_date(self, date):
        """Returns events due on the given date."""
        if self.get_user_preferences().show_owned_calendar:
            owner = [self.get_user().get_id()]
        else:
            owner = None
        return self.catalog_search(meta_type='Issue', due=[date,date+0.99999999], due_usage='range:min:max',
			state='open', tags=['issue-type:goal', 'issue-type:problem', 'issue-type:question'
				'issue-type:idea'], owners=owner,
				path='/'.join(self.getPhysicalPath()))

    security.declareProtected(id_permissions.view_issue_dealer, 'get_past_due_events')
    def get_past_due_events(self):
        """Returns events past their due date."""
        if self.get_user_preferences().show_owned_calendar:
            owner = [self.get_user().get_id()]
        else:
            owner = None
        return self.catalog_search(meta_type='Issue', due=[DateTime('1970-01-01'), DateTime()], due_usage='range:min:max',
			state='open', is_action_issue=True, owners=owner, sort_on='due',
				path='/'.join(self.getPhysicalPath()))

InitializeClass(base_calendar)
