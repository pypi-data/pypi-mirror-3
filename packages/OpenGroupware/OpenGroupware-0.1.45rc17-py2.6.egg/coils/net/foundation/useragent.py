# Copyright (c) 2009, 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

class UserAgent(object):

    def __init__(self, user_agent, request=None):
        # Parse user-agent stiring
        if (user_agent is None):
            user_agent = 'Generic'
        else:
            parts = user_agent.split('/')
            if (len(parts) > 1):
                self.agent_name    = parts[0].lower()
                self.agent_version = parts[1].lower()
            else:
                self.agent_name = parts[0].lower()
                self.agent_version = 'Unknown'
        # Default user-agent capacities
        self._escape_gets = False
        self._supports_301 = True
        self._supports_location = True
        self._supports_memos = False
        self._absolute_hrefs = False
        # Set special user-agent based capacities
        if ((self.agent_name in ['gvfs', 'curl', 'bionicmessage.net jgroupdav', 'mozilla',
                                 'microsoft-webdav-miniredir']) or
             (self.agent_name.startswith('microsoft data access internet publishing'))):
            self._supports_301 = False
            self._supports_location = False
            if ((self.agent_name in ('curl', 'microsoft-webdav-miniredir')) or
                (self.agent_name.startswith('microsoft data access internet publishing'))):
                self._absolute_hrefs = True
        if (self.agent_name in ['evolution']):
            self._supports_memos = True
        if (self.agent_name in ['bionicmessage.net jgroupdav']):
            self._escape_gets = True
        self.request = request

    @property
    def folder_content_type(self):
        if ((self.agent_name == 'microsoft-webdav-miniredir') or
            (self.agent_name.startswith('microsoft data access internet publishing'))):
            return'text/html'
        return 'unix/httpd-directory'

    def default_properties(self):
        if ((self.agent_name == 'microsoft-webdav-miniredir') or
            (self.agent_name.startswith('microsoft data access internet publishing'))):
            properties = [
                ( 'get_property_webdav_href',             u'DAV:', u'href',             u'webdav', 'D:href' ),
                ( 'get_property_webdav_getcontenttype',   u'DAV:', u'getcontenttype',   u'webdav', 'D:getcontenttype' ),
                ( 'get_property_webdav_getlastmodified',  u'DAV:', u'getlastmodified',  u'webdav', 'D:getlastmodified' ),
                ( 'get_property_webdav_creationdate',     u'DAV:', u'creationdate',     u'webdav', 'D:creationdate' ),
                ( 'get_property_webdav_displayname',      u'DAV:', u'displayname',      u'webdav', 'D:displayname' ),
                ( 'get_property_webdav_getcontentlength', u'DAV:', u'getcontentlength', u'webdav', 'D:getcontentlength' ),
                ( 'get_property_apache_executable',
                  u'http://apache.org/dav/props/',                 u'executable',       u'webdav',  'A:executable' ),
                ( 'get_property_webdav_resourcetype',     u'DAV:', u'resourcetype',     u'webdav',  'D:resourcetype' ) ]
            namespaces = { 'A': 'http://apache.org/dav/props/',
                           'D': 'DAV'
                         }

        else:
            properties = [
                ( 'get_property_webdav_name',             u'DAV:', u'name',             u'webdav', 'D:name' ),
                ( 'get_property_webdav_href',             u'DAV:', u'href',             u'webdav', 'D:href' ),
                ( 'get_property_webdav_getcontenttype',   u'DAV:', u'getcontenttype',   u'webdav', 'D:getcontenttype' ),
                ( 'get_property_webdav_contentclass',     u'DAV:', u'contentclass',     u'webdav', 'D:contentclass' ),
                ( 'get_property_webdav_getlastmodified',  u'DAV:', u'getlastmodified',  u'webdav', 'D:getlastmodified' ),
                ( 'get_property_webdav_getcontentlength', u'DAV:', u'getcontentlength', u'webdav', 'D:getcontentlength' ),
                ( 'get_property_webdav_iscollection',     u'DAV:', u'iscollection',     u'webdav', 'D:iscollection' ),
                ( 'get_property_webdav_displayname',      u'DAV:', u'displayname',      u'webdav', 'D:displayname' ),
                ( 'get_property_caldav_getctag',
                  u'urn:ietf:params:xml:ns:caldav',                u'getctag',          u'caldav', 'C:getctag' ),
                ( 'get_property_webdav_resourcetype',     u'DAV:', u'resourcetype',     u'webdav', 'D:resourcetype' ) ]
            namespaces =  { 'C': 'urn:ietf:params:xml:ns:caldav',
                            'D': 'DAV',
                            'G': 'http://groupdav.org/'
                          }
        return properties, namespaces

    @property
    def supports_301(self):
        return self._supports_301

    @property
    def supports_memos(self):
        return self._supports_memos

    @property
    def supports_location(self):
        return self._supports_location

    @property
    def absolute_hrefs(self):
        return self._absolute_hrefs

    def get_appropriate_href(self, href):
        if self._absolute_hrefs:
            if (UserAgent.__davServerName__ is None):
                server_name = self.request.server_name
            else:
                server_name = UserAgent.__davServerName__
            if (UserAgent.__discardPortOnAbsoluteURLs__):
                return u'http://{0}{1}'.format(server_name, href)
            else:
                return u'http://{0}:{1}{2}'.format(server_name, self.request.server_port, href)
        else:
            return href

    @property
    def escape_gets(self):
        return self._escape_gets