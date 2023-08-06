import AccessControl
from Globals import InitializeClass, Persistent
import types
import email
from Products.IssueDealer import id_config
import smtplib
from email.Header import decode_header
import re
import cStringIO
from email import Utils

from Products import ZCatalog, HTMLTools
import OFS
import Acquisition
from Products.IssueDealer import base, session_manager, add_gateway, permissions, issue_dealer
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from cgi import escape

from Globals import PersistentMapping
from persistent.list import PersistentList

import string, random

from Products.HTMLTools import html

from OFS.CopySupport import CopyContainer

issue_tag = re.compile('\[issue:\w+(:\w+)?\]')

def get_preferred_content_type(message_):
    """Returns the preferred content type (text/plain) if
    possible, otherwise returns the first type."""
    if message_.get_content_type() == 'multipart/alternative':
        for message in message_.get_payload():
            if message.get_content_type() == 'text/plain':
                return ('text/plain', message.get_payload(decode=True), message.get_param('name') or message.get_param('filename'))
        else:
            message = message_.get_payload(decode=True)[0]
            return (message.get_content_type(), message, message.get_param('name') or message.get_param('filename'))
    else:
        x = (message_.get_content_type(), message_.get_payload(decode=True), message_.get_param('name') or message_.get_param('filename'))
        #print 'x', x
        return x

def my_decode_header(header):
    my_string = ""
    for value, encoding in decode_header(header):
        my_string += value + ' '
    return my_string[:-1]

def get_message_sender(message):
    "Returns the sender of the email message."""
    for header in ('from', 'sender', 'reply-to'):
        value = message[header]
        if value:
            break
    if value:
        return Utils.parseaddr(value)
    else:
        try:
            return ('Sender', message.get_unixfrom().split()[1])
        except:
            return ('Sender unknown', 'unknown@localhost')

def get_recipients(message):
    """Returns a tuple with To and Cc recipients of the message."""
    try:
        to = Utils.getaddresses(message.get_all('to'))
    except TypError:
        to = ()
    try:
        cc = Utils.getaddresses(message.get_all('cc'))
    except TypeError:
        cc = ()
    return (to, cc)

def format_recipients(recipients):
    "Formats a sequence of recipients."
    formatted = ""
    for recipient in recipients:
        formatted += '%s <%s>, ' % recipient
    return formatted[:-2]

def get_parent_message_id(message):
    """Returns the message-id we're replying to, if any."""
    references = message['references']
    in_reply_to = message['in-reply-to']
    references = references.split()
    if references:
        if references[-1] == in_reply_to:
            return in_reply_to
        if not in_reply_to:
            return references[-1]
    if in_reply_to:
        return in_reply_to
    else:
        return None

verify_address_template = """Subject: Email verification needed
From: %s

A verification that you are not spamming the address

  %s

is needed.  If you do not verify your address, chances
are the message(s) you have sent will not get read.

Please go to

  %s

and enter the email address you're sending from, as well as
the other parts of the form.  Thank you.
"""

def manage_add_issue_dealer_mail_edit(self, id=None, title='', REQUEST=None):
    """Add a mail gateway."""
    if id is None:
        id = self.get_unique_id()
    issue_dealer_mail_ = issue_dealer_mail(id, title,
                   creator=self.get_user().get_id(),
                   owner=self.get_user().get_id())
    self._setObject(id, issue_dealer_mail_)
    issue_dealer_mail_ = self._getOb(id)
    issue_dealer_mail_.version = self.get_issue_dealer().filesystem_version
    if REQUEST is not None:
        REQUEST.RESPONSE.redirect(self.absolute_url() + '/' + id + '/edit')
    else:
        return issue_dealer_mail_

class issue_dealer_mail(
    ZCatalog.CatalogAwareness.CatalogAware,
    OFS.Folder.Folder,
    Persistent,
    Acquisition.Implicit,
    AccessControl.Role.RoleManager,
    base.base,
    session_manager.session_manager,
):
    "Mail handling gateway."

    security = AccessControl.ClassSecurityInfo()
    meta_type = 'Mail gateway'
    issue = ''
    unverified_tags = ()
    verified_tags = ()
    strip_unverified_tags = 1
    due_date = 1.0
    incoming_owners = ()

    security.declareProtected(permissions.manage_issue_dealer, 'edit')
    edit = PageTemplateFile('edit.pt', globals())
    deal = PageTemplateFile('deal.pt', globals())
    verified_senders = PageTemplateFile('verified_senders.pt', globals())
    verify_address = PageTemplateFile('verify_address.pt', globals())

    def __init__(self, id, title='Mail gateway', creator='', owner=''):
        self.id = id
        self.title = title
        self.creator = creator
        self.owner_ = owner
        self.skip_me_too = 1
        self.admin_email = ''
        self.recipients = ()
        self._message_id_issue_id = PersistentMapping()
        self.verified_senders_list = PersistentList()
        self.unverified_senders_list = PersistentList()
        self.list_address = ''
        self.issue = ''
        self.pending_approval_issue = ''
        self.pending_approval_queue = PersistentMapping()

    security.declareProtected(permissions.view_issue_dealer, 'get_admin_url')
    def get_admin_url(self):
        """Returns the adminstrator view."""
        return self.absolute_url() + '/deal'
 
    security.declareProtected(permissions.manage_issue_dealer, 'admin_edit')
    def admin_edit(self, id=None, title='', 
                   skip_me_too=0,
                   admin_email='',
                   recipients='',
                   issue='',
		   list_address='',
                   pending_approval_issue='',
		   verified_tags=(),
		   unverified_tags=(),
		   strip_unverified_tags=0,
                   due_date=1.0,
		   incoming_owners=(),
                   REQUEST=None):
        """Edits the gateway."""
        if id and id != self.id:
            self.getParentNode().manage_renameObjects(ids=[self.id], new_ids=[id])
            get_transaction().commit()
        self.title = title.strip()
        self.skip_me_too = skip_me_too
        self.admin_email = admin_email.strip()
        self.recipients = tuple(recipients.split())
        self.issue = issue.strip()
        self.list_address = list_address
        self.pending_approval_issue = pending_approval_issue.strip()
        self.verified_tags = PersistentList(map(lambda x: x.strip().replace(',', ':'),
		cStringIO.StringIO(verified_tags).readlines()))
        self.unverified_tags = PersistentList(map(lambda x: x.strip().replace(',', ':'),
		cStringIO.StringIO(unverified_tags).readlines()))
        self.strip_unverified_tags = strip_unverified_tags
        self.due_date = float(due_date)
        self.incoming_owners = PersistentList(incoming_owners)
        self.modified = DateTime()
        self.index_object()
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.get_admin_url())

    security.declareProtected(permissions.manage_issue_dealer, 'render_recipients_widget')
    def render_recipients_widget(self):
        "Renders the recipients widget."""
        html = "<textarea cols='40' rows='10' name='recipients'>"
        for recipient in self.recipients:
            html += escape(recipient) + '\n'
        return html + "</textarea>"

    security.declareProtected(permissions.manage_issue_dealer, 'render_verified_tags_widget')
    def render_verified_tags_widget(self):
        "Renders the verified tags widget."""
        html = "<textarea cols='40' rows='10' name='verified_tags'>"
        for verified_tag in self.verified_tags:
            html += escape(verified_tag) + '\n'
        return html + "</textarea>"

    security.declareProtected(permissions.manage_issue_dealer, 'render_unverified_tags_widget')
    def render_unverified_tags_widget(self):
        "Renders the unverified tags widget."""
        html = "<textarea cols='40' rows='10' name='unverified_tags'>"
        for unverified_tag in self.unverified_tags:
            html += escape(unverified_tag) + '\n'
        return html + "</textarea>"

    security.declareProtected(permissions.manage_issue_dealer, 'remove_verified_sender')
    def remove_verified_sender(self, email, RESPONSE=None):
        "Removes a verified sender"
        try:
            self.verified_senders_list.remove(email)
        except ValueError:
            pass
        if RESPONSE:
            RESPONSE.redirect('./verified_senders')

    def _handle_parts_and_issues(self, issue, subject, parts, sender, message):
        from Products.IssueDealer.issue import manage_add_issue
        recipients = get_recipients(message)
        to = format_recipients(recipients[0])
        cc = format_recipients(recipients[1])
        if parts[0][0] == 'text/html':
            issue.format = 'html'
            contents = ''
            if to:
                contents += 'To: %s<br />' % escape(to)
            if cc:
                contents += 'Cc: %s<br />' % escape(cc)
            if to or cc:
                contents += '<br />'
            contents += html.paranoid_clean(parts[0][1])
        elif parts[0][0] == 'text/plain' or (parts[0][0].split('/')[0] == 'text'):
            issue.format = 'text'
            contents = ''
            if to:
                contents += 'To: %s\n' % to
            if cc:
                contents += 'Cc: %s\n' % cc
            if to or cc:
                contents += '\n'
            contents += parts[0][1]
        else:
            # We have a file or something else
            issue.format = 'file'
        if issue.format == 'file':
            file = cStringIO.StringIO(parts[0][1])
            issue.manage_edit(title=subject, file=file, filename=parts[0][2])
        else:
            issue.manage_edit(title=subject, contents=contents)
        for part in parts[1:]:
            new_issue = manage_add_issue(issue, creator=sender[1])
            if part[2]:
                title = 'Attachment %s' % part[2]
            else:
                title = 'Attachment (%s)' % part[0]
            if part[0] == 'text/html':
                new_issue.format = 'html'
                contents = html.paranoid_clean(part[1])
            elif part[0] == 'text/plain' or (part[0].split('/')[0] == 'text'):
                new_issue.format = 'text'
                contents = part[1]
            else:
                # We have a file or something else
                new_issue.format = 'file'
            if new_issue.format == 'file':
                print part
                print parts
                file = cStringIO.StringIO(part[1])
                new_issue.manage_edit(title=title, file=file, filename=part[2])
            else:
                new_issue.manage_edit(title=title, contents=contents)

    def _send_copy_of_message(self, message, mfrom=''):
        " "
        message_recipients = []
        for recipient_set in get_recipients(message):
            message_recipients.extend(map(lambda x: x[1], recipient_set))
        mailto = list(self.recipients)
        for recipient in mailto[:]:
            if recipient in message_recipients:
                if self.skip_me_too:
                    mailto.remove(recipient)
        if mailto:
            connection = smtplib.SMTP(id_config.smtp)
            connection.sendmail(mfrom or self.admin_email, mailto, message.as_string())

    def _register_message_id_issue_id(self, message_id, issue_id):
        "Registers a message-id with a given issue id."
        self._message_id_issue_id[message_id] = issue_id

    def _ask_for_sender_verification(self, sender):
        """Sends an email asking for email verification."""
        message = verify_address_template % (sender, self.list_address, self.absolute_url() + '/verify_address')
        connection = smtplib.SMTP(id_config.smtp)
        connection.sendmail(self.admin_email, [sender], message)

    def _verify_sender(self, sender_email):
        if not (sender_email == self.admin_email or sender_email in self.recipients\
			 or sender_email in self.verified_senders_list):
            # Send message back asking for verification
            if not sender_email in self.unverified_senders_list:
                self.unverified_senders_list.append(sender_email)
            self._ask_for_sender_verification(sender_email)
        else:
            return 1

    security.declarePublic('process_incoming_mail')
    def process_incoming_mail(self, Mail=''):
        """Processes incoming emails."""
        # This method is too beeeg
        assert Mail
        from Products.IssueDealer.issue import manage_add_issue
        message = email.message_from_string(Mail)
        parts = []
        if message.get_content_type() == 'multipart/alternative':
            parts.append(get_preferred_content_type(message))
        else:
            payload = message.get_payload()
            print 'message', message
            #print 'payload', payload
            if type(payload) is types.ListType:
                for part in payload:
                    parts.append(get_preferred_content_type(part))
            else:
                parts.append((message.get_content_type(),
    			message.get_payload(decode=True)))
        subject = my_decode_header(message['subject'])
        sender = get_message_sender(message)
        match = issue_tag.search(subject)
        raw_tag = ''
        parent = None
        sender_email = sender[1]
        verified_sender = self._verify_sender(sender_email)
        if match or (message['message-id'] in self._message_id_issue_id.keys()):
            raw_tag = match.group()
            subject = subject.replace(raw_tag, '')
            try:
                issue_id = self._message_id_issue_id[get_parent_message_id(message)]
            except KeyError:
                issue_id = raw_tag[1:-1].split(':')[1]
            parent = self.get_object(issue_id).getObject()
        else:
            if self.issue:
                parent = self.get_object(self.issue).getObject()
            else:
                parent = self.get_issue_dealer()
        if verified_sender:
            issue = manage_add_issue(parent, creator=sender[1], owners=tuple(self.incoming_owners))
        else:
            if self.pending_approval_issue:
                unverified_parent = self.get_object(self.pending_approval_issue).getObject()
            else:
                unverified_parent = self.get_issue_dealer()
            issue = manage_add_issue(unverified_parent, creator=sender[1], owners=('unknown',))
            if not self.pending_approval_queue.has_key(sender[1]):
                self.pending_approval_queue[sender[1]] = PersistentList()
            self.pending_approval_queue[sender[1]].append((issue.id, parent.id))
	#print parts
        self._handle_parts_and_issues(issue, subject, parts, sender, message)
        self._register_message_id_issue_id(message['message-id'], issue.id)
        if verified_sender:
            issue.add_tags(self.verified_tags)
            if issue.is_action_issue() and self.due_date:
                issue.due = DateTime() + self.due_date
            issue.index_object()
            self._hand_off_email(issue, message=message, subject=subject)
        else:
            issue.add_tags(self.unverified_tags)
        return "TRUE"

    def _hand_off_email(self, issue, message=None, subject=None):
        " "
        if message is None:
            message = email.message_from_string(issue.render_contents_as_text())
            subject = issue.title
            mfrom = issue.creator
        else:
            mfrom = ''
        new_tag = ''
        #if raw_tag:
        #    new_tag = raw_tag # Just keep the tag
        #else:
        #    new_tag = '[issue:' + issue.id + ']'
        new_tag = '[issue:' + issue.id + ']'
        del message['subject']
        message['subject'] = subject + ' ' + new_tag
        if mfrom:
            del message['from']
            message['from'] = mfrom
        self._send_copy_of_message(message)

    def _update(self):
        if not hasattr(self.aq_base, 'verified_senders_list'):
            self.verified_senders_list = PersistentList()
            self.unverified_senders_list = PersistentList()
        if not hasattr(self.aq_base, 'list_address'):
            self.list_address = ''
        if not hasattr(self.aq_base, 'pending_approval_issue'):
            self.pending_approval_issue = ''
        if not hasattr(self.aq_base, 'pending_approval_queue'):
            self.pending_approval_queue = PersistentMapping()

    security.declarePublic('verify_email_address')
    def verify_email_address(self, email, passphrase, real_passphrase):
        if passphrase == real_passphrase:
            if email in self.unverified_senders_list:
                self.unverified_senders_list.remove(email)
                if not email in self.verified_senders_list:
                    self.verified_senders_list.append(email)
                    for issue, parent in self.pending_approval_queue[email]:
                        issue = self.get_object(issue).getObject()
                        if self.strip_unverified_tags:
                            issue.remove_tags(self.unverified_tags)
                        issue.add_tags(self.verified_tags)
                        if issue.is_action_issue() and self.due_date:
                            issue.due = DateTime() + self.due_date
                        issue.owners = PersistentList(self.incoming_owners)
                        issue.index_object()
                        parent = self.get_object(parent).getObject()
                        # Dir-tey, but it works :)
                        hacked = CopyContainer._verifyObjectPaste
                        CopyContainer._verifyObjectPaste = lambda x,y,validate_src=None: 1
                        parent.manage_pasteObjects(issue.getParentNode().manage_cutObjects(ids=[issue.id]))
                        CopyContainer._verifyObjectPaste = hacked
                        self._hand_off_email(issue)
                    del self.pending_approval_queue[email]
                    return 1
        else:
            return 0

    security.declarePublic('generate_passphrase')
    def generate_passphrase(self):
        "Generates a simple passphrase."""
        passphrase = ""
        for x in range(6):
            passphrase += random.choice(string.ascii_letters)
        return "<input type='hidden' name='real_passphrase' value='%s' />%s" % (passphrase, passphrase)

InitializeClass(issue_dealer_mail)
issue_dealer.issue_dealer.manage_add_issue_dealer_mail_edit = manage_add_issue_dealer_mail_edit
issue_dealer.issue_dealer.all_meta_types = issue_dealer.issue_dealer.all_meta_types + [
    {'visibility': 'Global',
     'interfaces': [],
     'action': 'manage_add_issue_dealer_mail_edit',
     'permission': 'Add Mail gateway',
     'name': 'Mail gateway',
     'product': 'Issue Dealer',
     'instance': ''},]
add_gateway(issue_dealer_mail, manage_add_issue_dealer_mail_edit)
