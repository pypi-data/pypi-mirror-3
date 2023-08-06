import AccessControl
import permissions as id_permissions
from cgi import escape
from Globals import InitializeClass
import utilities
from Products.laf import url_utilities

class base_sequence:

    security = AccessControl.ClassSecurityInfo()

    security.declareProtected(id_permissions.view_issue_dealer, 'get_sequence_items')
    def get_sequence_items(self, sequence):
        """Returns the sequence items, based on start and size."""
        request = self.get_request()
        return sequence[int(request.get('start', 0)):int(request.get('start', 0)) + int(request.get('size', 10))]

    security.declareProtected(id_permissions.view_issue_dealer, 'render_previous')
    def render_previous(self, sequence, url=None, html_quote=1):
        """Renders previous html for a sequence."""
        request = self.get_request()
        start = int(request.get('start', 0))
        size = int(request.get('size', 10))
        if start == 0: return "&lt;&lt; Previous"
        else: start -= size
        qs = request.get('QUERY_STRING', '')
        qs = self.create_query_string(qs, replace=1, start=start, size=size)
        url = url_utilities.build_url(request['URL0'], qs)
        return '<a href="%s">&lt;&lt; Previous</a>' % escape(url)

    security.declareProtected(id_permissions.view_issue_dealer, 'render_batches')
    def render_batches(self, sequence, start=None, size=None):
        """Renders batches html for a sequence."""
        request = self.get_request()
        start = start or int(request.get('start', 0))
        size = size or int(request.get('size', 10))
        displayed = batches = 0
        html = ""
        qs = request.get('QUERY_STRING', '')
        if (start / size) > 5 and (len(sequence) / size) > 10:
            qs = self.create_query_string(qs, replace=1, start=0, size=size)
            url = url_utilities.build_url(request['URL0'], qs)
            html += '<a href="%s">%s</a> ' % (escape(url), 1) + ' ... '
        for start_ in range(0, len(sequence), size):
            displayed = 1
            qs = self.create_query_string(qs, replace=1, start=start_, size=size)
            url = url_utilities.build_url(request['URL0'], qs)
            html_ = '<a href="%s">%s</a> ' % (escape(url), start_/size + 1)
            if start_ == start:
                html += "<b>" + html_ + "</b>"
            elif start_ >= size * ((start/size) - 5) and start_ <= size * ((start/size) + 5):
                html += html_
            elif (start / size) < 5 and (start_ / size) < 10:
                html += html_
            elif (start / size) > (len(sequence) / size) - 5 and \
		(len(sequence) / size) < (start_ / size) + 10:
                html += html_
            else: displayed = 0
        else:
            if not displayed:
                html += ' ... ' + html_
        return html

    security.declareProtected(id_permissions.view_issue_dealer, 'render_previous')
    def render_next(self, sequence, url=None, html_quote=1):
        """Renders previous html for a sequence."""
        request = self.get_request()
        start = int(request.get('start', 0))
        size = int(request.get('size', 10))
        if (start + size) >= len(sequence): return "Next &gt;&gt;"
        else: start += size
        qs = request.get('QUERY_STRING', '')
        qs = self.create_query_string(qs, replace=1, start=start, size=size)
        url = url_utilities.build_url(request['URL0'], qs)
        return '<a href="%s">Next &gt;&gt;</a>' % escape(url)

InitializeClass(base_sequence)
