from Globals import InitializeClass
import string

def stop(object):
    return getattr(object, 'stop_breadcrumbs', 0)

class laf_base:

    def render_breadcrumbs(self, cut=0, klass='', separator=' &raquo; ', hyperlink=1, html=1, suffix='', stop=stop):
        """Renders breadcrumbs."""
        parents = self.get_parents(stop=stop)
        breadcrumbs = []
        for parent in parents:
            # This conditional is needed to play nice with
            # objects that don't inherit from this class.
            if hasattr(parent, 'aq_base') and hasattr(parent.aq_base, 'get_title'):
                title = parent.get_title()
            else:
                if parent.title: title = parent.title
                else: title = parent.id.capitalize()
            try:
                if hyperlink:
		    if suffix:
			# To trip AttributeError if we're out of context
                        breadcrumbs.append(self.create_hyperlink(
                            parent.absolute_url() + suffix, title, klass="navigation"))
                    else:
                        breadcrumbs.append(self.create_hyperlink(
                            parent.get_admin_url(), title, klass="navigation"))
                else:
                    breadcrumbs.append(title)
            except AttributeError:
                break
        breadcrumbs.reverse()
        if cut:
            breadcrumbs = breadcrumbs[:-cut]
        if html:
            return """<div id="breadcrumbs">""" + \
                   string.join(breadcrumbs, separator) + \
                   """</div>"""
        else:
            return string.join(breadcrumbs, separator)

InitializeClass(laf_base)