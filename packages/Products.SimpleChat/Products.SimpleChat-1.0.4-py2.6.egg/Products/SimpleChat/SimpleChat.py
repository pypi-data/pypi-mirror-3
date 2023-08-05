from Globals import InitializeClass, DTMLFile
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
import OFS
from CreateAppendGet.CAG import CAG
from AccessControl import getSecurityManager
import urllib
from DateTime import DateTime
from persistent.mapping import PersistentMapping
from persistent.list import PersistentList
import AccessControl
#from zope.i18nmessageid import MessageFactory 
#_ = MessageFactory('SimpleChat')
import urlparse

from zope.i18n import translate

def _(msgid, request):
    language = request['LANGUAGE']
    return translate(msgid, domain='SimpleChat', target_language=language, context=request)

manage_add_simple_chat_form = PageTemplateFile('skins/simple_chat/simple_chat_add.pt', globals())

def get_remote_address(request):
    remote = request.get('HTTP_X_FORWARDED_FOR', '')
    remote2 = request.get('REMOTE_ADDR', '')
    if remote:
        return True, remote
    elif remote2:
        return True, remote2
    else:
        return False, _('No IP address found, dumping request as HTML: ', request) + str(request)

def manage_add_simple_chat(self, id, title='', REQUEST=None):
    """Add an Issue Dealer."""
    self._setObject(id, SimpleChat(id, title))
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

View = 'View'
Manage = 'Manage'

report_mail_template = """Subject: User reported chat content

Hi.

The following post was identified as being reportable,
please deal with it as appropriate.

%s

%s

==============================================

Valid remote address: %s

%s

"""

import scconfig

def since(stamp):
    # To avoid UnboundLocalError
    archive, index = map(lambda x: int(x), stamp.split('-'))
    def since_function(entry, archive=archive, index=index):
        # Exception handled for old format
        return entry[0] == archive and entry[1] == index
    return since_function

class SimpleChat(OFS.Folder.Folder, CAG):

    meta_type = 'SimpleChat'

    security = AccessControl.ClassSecurityInfo()

    index_html = PageTemplateFile('skins/simple_chat/simple_chat_index.pt', globals())
    logs = PageTemplateFile('skins/simple_chat/simple_chat_logs.pt', globals())
    report = PageTemplateFile('skins/simple_chat/simple_chat_report.pt', globals())
    report_submit = PageTemplateFile('skins/simple_chat/simple_chat_report_submit.pt', globals())
    ban = PageTemplateFile('skins/simple_chat/simple_chat_ban.pt', globals())
    banned = PageTemplateFile('skins/simple_chat/simple_chat_banned.pt', globals())
    jquery = DTMLFile('skins/simple_chat/jquery.min.js', globals())

    security.declareProtected(View, 'index_html', 'logs', 'report', 'report_submit', 'jquery')
    security.declareProtected(Manage, 'ban', 'banned')

    chat_blocked = False

    security.declareProtected(Manage, 'toggle_chat')
    def toggle_chat(self, REQUEST, RESPONSE, confirm=False):
        """Toggle availability of chat."""
        if not confirm:
            RESPONSE.redirect(self.absolute_url() + '?confirm_block=True#confirm_block')
            return
        self.chat_blocked = not self.chat_blocked
        if self.chat_blocked:
            message = ''
        else:
            message = _(u'Simple chat has been unblocked', REQUEST)
        RESPONSE.redirect(self.absolute_url() + '?message=' + urllib.quote(message))

    security.declareProtected(View, 'ajax_update')
    def ajax_update(self, stamp, REQUEST, RESPONSE):
        """Returns XML version of chat updates and new timestamp"""
        RESPONSE.setHeader('content-type', 'text/html')
        entries = self.CAG_get_numbered_since(since(stamp))
        try:
            # Cut off old line
            entries = entries[1:]
        except IndexError:
            # No entries, nothing on index
            pass
        xml = ""
        archive, index = map(lambda x: int(x), stamp.split('-'))
        for item in entries:
            archive, index = item[0], item[1]
            entry = item[2]
            try:
                xml += """<div id='chatline'><span>""" + entry[3].strftime('%Y-%m-%d %H:%M:%S') + "</span>"
            except IndexError:
                # Old format
                pass
            xml += ' <span>%s: %s</span></div>\n' % (entry[0], entry[2])
        else:
            stamp = archive, index
        xml += "<form name='refresh_form' id='refresh_form'><input type='hidden' name='stamp' value='%s' /></form>" % \
            (str(stamp[0]) + '-' + str(stamp[1]))
        # Chat Ajax updates are set to every 30 seconds.  So
        # touching the username every hour and half hour should
        # be enough without bloating the database.
        #
        # Might bring stress on the database and conflict errors
        # when everything hits but let's see what happens.
        minute = DateTime().minute()
        if minute in (0, 59):
            self.touch_address_and_username()
        if self.chat_blocked:
            xml += _(u'Simple chat has been blocked', REQUEST) + '<br />'
        return xml

    security.declareProtected(Manage, 'ban_remove')
    def ban_remove(self, IP, REQUEST, RESPONSE):
        """Remove ban."""
        for IP_, date, comment in self.banned_ips:
            if IP_ == IP:
                self.banned_ips.remove((IP_, date, comment))
                RESPONSE.redirect(self.absolute_url() + '/banned?message=' + urllib.quote(_(u'Ban removed', REQUEST)))
                return
        RESPONSE.redirect(self.absolute_url() + '/banned?message=' + urllib.quote(_(u'No ban removed, IP not found', REQUEST)))

    security.declareProtected(View, 'send_report_email')
    def send_report_email(self):
        """Sends an abuse report email."""
        request = self.REQUEST
        a = str(request.a)
        i = str(request.i)
        uri =  self.get_simple_chat().absolute_url() + \
            '/logs?a:int=' + a + '&i:int=' + i + '#' + a + '-' + i
        remote_address_valid, address = get_remote_address(request)
        email = _(report_mail_template, request) % (uri, request.comments, remote_address_valid, address)
        scconfig.send_email(email)

    security.declareProtected(View, 'get_simple_chat')
    def get_simple_chat(self):
        # No __doc__ string so it can't be called through the web.

        # """Returns simple chat instance."""
        return self

    security.declareProtected(View, 'get_banned_ips')
    def get_banned_ips(self):
        # No __doc__ string so it can't be called through the web.

        # """Returns a dictionary of banned IPs."""

        # Oh well, it is nice to develop on
        # the original object instance.  :)
        banned_ips = []
        if not hasattr(self, 'banned_ips'):
            self.banned_ips = PersistentList()
        for IP, date, comment in self.banned_ips:
            # IPs are banned for one hour
            if (int(date) + 3600) > int(DateTime()):
                banned_ips.append((IP, date, comment))
        return banned_ips

    security.declareProtected(Manage, 'ban_submit')
    def ban_submit(self, a, i, comments, REQUEST, RESPONSE):
        """Bans an IP address, leaving comments as well."""
        chatline = self.CAG_get_numbered_item(a, i)
        try:
            username, IP, text, date = chatline
        except ValueError:
            # Old format without date
            username, IP, text = chatline
        self.ban_ip(IP, comments.decode('utf-8') + "\n\n" + _(u"Offending chatline", REQUEST).decode('utf-8') + ":\n\n" + text.decode('utf-8'))
        RESPONSE.redirect(self.absolute_url() + '?message=' + urllib.quote(_(u"User/IP successfully banned", REQUEST)))

    security.declareProtected(Manage, 'ban_ip')
    def ban_ip(self, IP, comment=""):
        """Bans an IP address."""
        IPs = self.get_banned_ips()
        if not IP in map(lambda x: x[0], IPs):
            self.banned_ips.append((IP, DateTime(), comment))

    security.declareProtected(View, 'is_banned')
    def is_banned(self):
        """Returns a truth value and message if banned."""
        request = self.REQUEST
        valid, remote = get_remote_address(request)
        if not valid:
            return False, '', remote
        banned_ips = self.get_banned_ips()
        for IP, date, comment in banned_ips:
            if IP == remote:
                return True, comment, IP
        else:
            return False, '', remote

    security.declareProtected(View, 'get_address_and_usernames')  
    def get_address_and_usernames(self):
        # No __doc__ string so it can't be called through the web.

        # Returns valid address and username mappings.
        items = PersistentMapping()
        if not hasattr(self.aq_base, 'address_and_username'):
            self.address_and_username = PersistentMapping()
        for key, value in self.address_and_username.items():
            items[key] = PersistentList()
            for username, date in value:
                if (int(date) + 7200) > int(DateTime()):
                    items[key].append((username, date))
        if items != self.address_and_username:
            self.address_and_username = items
        return items

    security.declareProtected(View, 'register_address_and_username')
    def register_address_and_username(self, remote_address, username):
        # No __doc__ string so it can't be called through the web.

        # """Registers a username/IP combo."""
        if not self.address_and_username.has_key(remote_address):
            self.address_and_username[remote_address] = PersistentList()
        self.address_and_username[remote_address].append((username, DateTime()))

    security.declareProtected(View, 'touch_address_and_username')
    def touch_address_and_username(self, remote_address=None, username=None):
        # No __doc__ string so it can't be called through the web.

        # """Touch and make address/username valid for another 2 hours."""
        if None in (remote_address, username):
            request = self.REQUEST
            valid, remote_address = get_remote_address(request)
            valid2, username, message = self.get_username(request)
            if not valid and valid2:
                return False
        for index in range(len(self.address_and_username.get(remote_address, []))):
            if username == self.address_and_username[remote_address][index][0]:
                self.address_and_username[remote_address][index] = (username, DateTime())
        return True

    security.declareProtected(View, 'chat_username_submit')
    def chat_username_submit(self, REQUEST, RESPONSE):
        """ """
        username = REQUEST.get('username')
        address_and_usernames = self.get_address_and_usernames().values()
        try:
            registered_usernames = map(lambda x: (len(x) and x[0]) or '', address_and_usernames)
        except IndexError:
            raise str((self.address_and_username, address_and_usernames))
        message = ""
        remote_address_valid, remote_address = get_remote_address(REQUEST)
        path = urlparse.urlparse(self.get_simple_chat().absolute_url())[2]
        if username in registered_usernames:
            count = 1
            while True:
                temporary_username = username + '-' + str(count) 
                if not temporary_username in registered_usernames:
                    RESPONSE.setCookie('username', temporary_username, path=path)
                    self.register_address_and_username(remote_address, username)
                    break
        else:
            if remote_address_valid:
                RESPONSE.setCookie('username', username, path=path)
                self.register_address_and_username(remote_address, username)
            else:
                message = _(u"No valid remote address, contact site administrator", REQUEST)
        RESPONSE.redirect(self.absolute_url()+'?message='+urllib.quote(message))

    security.declareProtected(View, 'chat_submit')
    def chat_submit(self, text, REQUEST, RESPONSE, ajax=False, stamp='0-0'):
        """Handles the chat string entered by a user."""
        if self.is_banned()[0]:
            RESPONSE.redirect(self.absolute_url() + '?message=' + urllib.quote(
                    _(u'Sorry, banned users (IPs) cannot make comments', REQUEST)))
            return
        if self.chat_blocked:
            RESPONSE.redirect(self.absolute_url() + '?message=' + urllib.quote(
                    _(u'Sorry, simple chat has been blocked', REQUEST)))
            return
        valid_address, IP_or_hostname =  get_remote_address(REQUEST)
        valid, username, message = self.get_username(REQUEST)
        message = ""
        if not valid:
            message = _(u"Not a valid username. ", REQUEST) + message
        if not valid_address:
            message += _(u" No valid user address.  Please contact site administrator", REQUEST)
        self.CAG_append((username, IP_or_hostname, text, DateTime()))
        if not ajax:
            RESPONSE.redirect(self.absolute_url() + '/?message=' + urllib.quote(message) + '&stamp2=' + urllib.quote(stamp) + '#archive-index-' + urllib.quote(stamp))
        else:
            return "Success!"

    security.declareProtected(View, 'get_username')
    def get_username(self, request, REQUEST=None):
        """Returns the participant username."""
        if not request: request = REQUEST
        username = request.cookies.get('username', None)
        if not username:
            username = str(getSecurityManager().getUser())
            if str(username) != 'Anonymous User':
                return True, str(username), ''
            else:
                return False, str(username), ''
        if username:
            addresses_and_usernames = self.get_address_and_usernames()
            if not username and not request.get('username', ''):
                return False, '', _(u'Register username below', request)
            remote_address_valid, remote_address = get_remote_address(request)
            if not remote_address_valid:
                return False, '', _(u'No remote IP address found, contact site administrator', request)
            if addresses_and_usernames.has_key(remote_address):
                if username in map(lambda x: x[0], addresses_and_usernames.get(remote_address, [])):
                    return True, username, ''
                else:
                    return False, username, _(u'Wrong IP address, if you changed location/IP, please register again with a different username', request)
            else:
                self.register_address_and_username(remote_address, username)
                return True, username, ''

    security.declareProtected(View, 'has_remote_address')            
    def has_remote_address(self, request):
        return request.get('HTTP_X_FORWARDED_FOR', '') or request.get('REMOTE_ADDR', '')

    def __init__(self, id, title):
        OFS.Folder.Folder.__init__.im_func(self, id)
        CAG.__init__.im_func(self, id, title)
        self.address_and_username = PersistentMapping()

    def getPreferredLanguage(self):
        """Returns the preferred language, works outside of Plone as well."""
        request = self.REQUEST
        if request.has_key('LANGUAGE_TOOL'):
            return request['LANGUAGE_TOOL'].getLanguageBindings()[0]
        else:
            try:
                return request['LANGUAGE']
            except IndexError:
                return 'en'
            except KeyError:
                return 'en'

InitializeClass(SimpleChat)
