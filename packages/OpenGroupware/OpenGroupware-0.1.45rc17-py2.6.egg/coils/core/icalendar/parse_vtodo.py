#
# Copyright (c) 2010, 2011 Adam Tauno Williams <awilliam@whitemice.org>
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
import datetime, pytz, re, hashlib, base64
import coils.foundation.api.vobject as vobject

def hash_for_data(value_):
        hash_ = hashlib.sha512()
        hash_.update(value_)
        return hash_.hexdigest()

def take_integer_value(values, key, name, vevent, default=None):
    key = key.replace('-', '_')
    if (hasattr(vevent.key)):
        try:
            values[name] = int(getattr(vevent, key).value)
        except:
            values[name] = default


def take_string_value(values, key, name, vevent, default=None):
    key = key.replace('-', '_')
    if (hasattr(vevent.key)):
        try:
            values[name] = str(getattr(vevent, key).value)
        except:
            values[name] = default


def find_attendee(ctx, email, log):
    if (len(email.strip()) < 6):
        #E-Mail address is impossibly short, don't even bother
        return None
    contacts = ctx.run_command('contact::get', email=email)
    if (len(contacts) == 1):
        contact_id = contacts[0].object_id
        log.debug('Found contact objectId#{0} for e-mail address {1}'.format(contact_id, email))
        return contact_id
    elif (len(contacts) > 1):
        log.warn('Multiple contacts found for e-mail address {0}'.format(email))
    else:
        log.warn('No contact found for e-mail address {0}'.format(email))
    teams = ctx.run_command('team::get', email=email)
    if (teams):
        if (len(teams) > 1):
            log.warn('Multiple teams found for e-mail address {0}'.format(email))
        return teams[0].object_id
    resources = ctx.run_command('resource::get', email=email)
    if (resources):
        if (len(resources) > 1):
            log.warn('Multiple resources found for e-mail address {0}'.format(email))
        return resources[0].object_id
    return None


def parse_attendee(line, ctx, log):
    # Attemdee
    pass

"""
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//PYVOBJECT//NONSGML Version 1//EN
BEGIN:VTODO
DESCRIPTION:*****************
DTSTART:20100716T094709Z
DUE:20100723T094709Z
ORGANIZER;CUTYPE=INDIVIDUAL;CN=Adam Tauno
  Williams:MAILTO:awilliam@whitemice.org
PERCENT-COMPLETE:0
PRIORITY:1
STATUS:NEEDS-ACTION
SUMMARY:*************************
UID:coils://Task/15349830
URL:http://**************/Tasks/view/15349830/History/
X-COILS-KIND:None
X-COILS-PROJECT;X-COILS-PROJECT-ID=1025770:************
END:VTODO
END:VCALENDAR
"""

def parse_vtodo(event, ctx, log, starts=[], duration=None, **params):
    # NOTE: vObject is kind enough to give us timezone aware datetimes from
    # start and end elements.  So this utz_tc value is used to convert those
    # TZ aware values to UTC for internal storage.
    utc_tz = pytz.timezone('UTC')
    values = {}
    for line in event.lines():
        if line.name == 'UID':
            keys = line.value.split('/')
            if (keys[0] == 'coils:'):
                if (keys[len(keys) - 1].isdigit()):
                    values['object_id'] = int(keys[len(keys) - 1])
        elif line.name == 'STATUS':
            if (line.value == 'NEEDS-ACTION'):
                values['status'] = '00_created'
            elif (line.value == 'IN-PROCESS'):
                values['status'] = '20_processing'
            elif (line.value == 'CANCELLED'):
                values['status'] = '02_rejected'
            elif (line.value == 'COMPLETED'):
                values['status'] = '25_done'
        elif line.name == 'ATTENDEE':
            pass
        elif line.name == 'SUMMARY':
            values['title'] = line.value
        elif line.name == 'DESCRIPTION':
            values['comment'] = line.value
        elif line.name == 'PERCENT-COMPLETE':
            # HACK: Complete must be a multiple of 10; like 10, 20, 30, 40,...
            if (line.value.isdigit()):
                values['complete'] = int((int(line.value) / 10) * 10)
        elif line.name == 'PRIORITY':
            priority = int(line.value)
            # TODO: Translate priority value
            values['priority'] = priority
        elif line.name == 'ATTACH':
            # TODO: Implement storing of attachments, of catching changes to attachments
            #       We probably need a SHA checksum for this too work
            ''' ATTACH;VALUE=BINARY;
                       ENCODING=BASE64;
                       X-EVOLUTION-CALDAV-ATTACHMENT-NAME=curl-json-rpc.php:
                         PD9QSFAKCmZ1bmN0aW9uIHpPR0lKU09OUlBDQ2FsbCgkdXNlcm5hbWUsICRwYXNzd29yZCwgJG
                         1ldGhvZCwgJHBhcmFtcywgCiAgICAgICAgICAgICAgICAgICAgICAgICAkaWQ9bnVsbCwgCiAg ... '''
            if ((line.params.get('VALUE', ['NOTBINARY'])[0] == 'BINARY') and
                (line.params.get('ENCODING', ['NOTBASE64'])[0] == 'BASE64')):
                if '_ATTACHMENTS' not in values:
                    values['_ATTACHMENTS'] = [ ]
                # Try to get at attachment name using one of the following attributes
                for attr in ('X-EVOLUTION-CALDAV-ATTACHMENT-NAME', 'X-ORACLE-FILENAME', 'X-COILS-FILENAME'):
                    if attr in line.params:
                        name_ = line.params[attr][0]
                        break
                else:
                    name_ = None
                data_ = base64.decodestring(line.value)
                hash_ = hash_for_data(data_)
                size_ = len(data_)
                mime_ = line.params.get('FMTTYPE', ['application/octet-stream'])[0]
                values['_ATTACHMENTS'].append( { 'entityName': 'Attachment',
                                                'sha512checksum': hash_,
                                                'data': data_,
                                                'name': name_,
                                                'mimetype': mime_,
                                                'size': size_ } )
            else:
                raise CoilsException('Unable to parse CalDAV ATTACH; not a binary attachment.')
        elif line.name == 'CATEGORIES':
            value = None
            if isinstance(line.value, list):
                if value:
                    value = line.value[0].strip()
                else:
                    value = ''
            elif isinstance(line.value, basestring):
                value = line.value.strip()
            if value:
                value = value.replace('\,', ',')
                value = value.split(',')
                value = ','.join([x.strip() for x in value])
                values['category'] = value
        elif line.name == 'ORGANIZER':
            # TODO: This should only be available to someone with the HELPDESK role
            pass
        elif line.name == 'DUE':
            # TODO: 'datetime.date' object has no attribute 'astimezone'
            values['end'] = line.value.astimezone(utc_tz)
        elif line.name == 'DTSTART':
            # TODO: 'datetime.date' object has no attribute 'astimezone'
            values['start'] = line.value.astimezone(utc_tz)
        elif line.name == 'X-COILS-PROJECT':
            # TODO: Check for project id parameter
            pass
        elif line.name =='X-COILS-KIND':
            values['kind'] = line.value
        else:
            # TODO: Save unknown properties as properties so we can put them back
            pass
    if ('object_id' not in values):
        #TODO Can we find other ways to try to find a pre-existing task if the
        #      retarted client dropped the UID attribute [Do not trust clients!]
        pass
    #import pprint
    #print '____begin_values___'
    #pprint.pprint(values)
    #print '____end_values___'
    #if '_ATTACHMENTS' in values:
    #    print '{0} attachments found'.format(len(values['_ATTACHMENTS']))
    #else:
    #    print 'No attachments found'
    return [ values ]
