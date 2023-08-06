import AccessControl
from Products.IssueDealer import base, image
from Products import HTMLTools
import time, cStringIO, cgi, types
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
try:
    from elementtree import ElementTree
except ImportError:
    ElementTree = None
import base64
import permissions
import re
from Globals import InitializeClass

class importers:
    """Mixin class to add importers to the Issue Dealer."""

    security = AccessControl.ClassSecurityInfo()
    security.declareProtected(permissions.add_edit_issues_and_relations, 'import_web_page_form', 'import_web_page',
	'import_web_page', 'import_xml_dump_form', 'import_xml_dump', 'importers')
    security.declareProtected(permissions.view_issue_dealer, 'get_importers')

    importers = PageTemplateFile('skins/issue_dealer/issue_dealer_importers.pt', globals())
    import_web_page_form = PageTemplateFile('skins/issue_dealer/issue_dealer_import_web_page_form.pt', globals())
    import_xml_dump_form = PageTemplateFile('skins/issue_dealer/issue_dealer_import_xml_dump_form.pt', globals())

    def get_importers(self):
        """Returns a list of available importers and their initial method."""
        importers = [{'title':'Web page importer', 'url':'import_web_page_form'}]
        if ElementTree:
            importers.append({'title':'Issue/Relation XML', 'url':'import_xml_dump_form'})
        return importers

    def import_web_page(self, urls, strip_tags=[]):
        """Imports the given URLs as an Issues with images."""
	issue = None
        response = self.get_response()
        response.setHeader('content-type', 'text/html')
        response.write("""<html><head><title>Importing web page(s)..</title>%s</head><body><pre style="padding: 2em;">""" % \
		("""<link rel="Stylesheet" type="text/css"
			href="%s" />""" % (self.get_issue_dealer().absolute_url() + '/style'))
	)
        for url in urls:
            if not url.strip(): continue
            try:
                issue = self._import_web_page(url, out=response, strip_tags=strip_tags)
            except:
                response.write('Failed to get web page..')
                import sys, traceback, string
                type, val, tb = sys.exc_info()
                response.write(cgi.escape(string.join(
                    traceback.format_exception(type, val, tb), '')))
                response.write('</pre><br /><br />')
        if issue:
            form_url = issue.get_admin_url()
        else:
            form_url = self.get_issue_dealer().get_admin_url()
        response.write("""</pre><form action="%s" method="post">&nbsp;&nbsp;&nbsp;&nbsp;
		<input type="submit" value=" OK " class="issueDealer" /></form></body></html>""" % form_url)
        response.flush()

    def import_xml_dump(self, file):
        """Imports the given file and creates issues and relations."""
        if ElementTree:
            x = ElementTree.parse(file)
            root = x.getroot()
            map(self._import_xml_dump, filter(lambda x: x.tag in ('issue', 'relation'), root))
        self.get_response().redirect(self.get_admin_url())
      
    def _import_xml_dump(self, item):
        children = item.getchildren()
        objects = []
        title = ''
        order = None
        contents = ''
        object = None
        filename = encoding = ''
	dependency_type = None
        for child in children:
            if child.tag in ('issue', 'relation'):
                objects.append(child)
            if child.tag == 'title':
		title = child.text or ''
            if child.tag == 'order':
                order = child.text or ''
            if child.tag == 'contents':
		contents = child.text or ''
                filename = child.attrib.get('filename', '')
                encoding = child.attrib.get('encoding', '')
	    if child.tag == 'dependency_type':
		dependency_type = child.text
        title = title.encode('utf-8')
        contents = contents.encode('utf-8')
        filename = filename.encode('utf-8')
        encoding = filename.encode('utf-8')
        if item.tag == 'issue':
            object = self.manage_add_issue(id=item.attrib['id'])
            if object is None:
                object = self[item.attrib['id']]
            for key, value in item.attrib.items():
                exec('object.%s = value.encode("utf-8")' % key)
            object.modified = DateTime(object.modified)
	    object.deleted = int(object.deleted)
            object.title = title
            object.order = order.split(',')
            if object.format == 'file':
                object.manage_addFile(filename, base64.decodestring(contents))
                object.filename = filename
            else:
                object.contents = contents
        elif item.tag == 'relation':
            object = self.manage_add_relation(id=item.attrib['id'])
            for key, value in item.attrib.items():
                exec('object.%s = value.encode("utf-8")' % key)
            object.modified = DateTime(object.modified)
	    object.deleted = int(object.deleted)
            object.title = title
            object.order = order.split(',')
	    if dependency_type:
		object.dependency = 1
		object.dependency_type = dependency_type
        else:
            raise item.tag
        object.index_object()
        for object_ in objects:
            object._import_xml_dump(object_)
            get_transaction().commit(1)

    def _import_web_page(self, url, out=None, strip_tags=[]):
        data = HTMLTools.html.fetch_webpage(url, out=out)
        image_ids = {}
        for source in data['images'].keys():
            image_ids[source] = self.get_unique_id()
            time.sleep(0.01)
        page = data['page'][0]
        image_url = self.get_issue_dealer().absolute_url() + '/image?id='
        for source, id in data['images'].items():
            page = page.replace(source, image_url + image_ids[source])
        for tag in strip_tags:
            start = re.compile('<%s.*?>' % tag, re.I | re.M | re.S)
            end = re.compile('</%s.*?>' % tag, re.I | re.M | re.S)
            for match in start.findall(page):
                page = page.replace(match, '')
            for match in end.findall(page):
                page = page.replace(match, '')
        issue = self.manage_add_issue(format='html', title=data['title'], tags='info')
        for source, image_ in data['images'].items():
            id = image_ids[source]
            image.add_image(issue, id=id, file=cStringIO.StringIO(image_[0]))
        issue.contents = page
        get_transaction().commit()
        issue.index_object()
        return issue

InitializeClass(importers)