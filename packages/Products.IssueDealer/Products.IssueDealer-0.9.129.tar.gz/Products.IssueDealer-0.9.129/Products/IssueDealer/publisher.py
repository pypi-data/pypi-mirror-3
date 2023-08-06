from Products import IssueDealerExtensions

def get_custom_remote_html(self):
    """Returns custom HTML for the remote."""
    html = ""
    if self.meta_type == 'Issue':
        return html + """<a href="publish" class="button" title="Publish issue">Publish</a><a href="#" id="toggle3" onclick="toggle('3'); return false;" class="button">+</a>"""
    else:
        return html

IssueDealerExtensions.add_button(get_custom_remote_html)
