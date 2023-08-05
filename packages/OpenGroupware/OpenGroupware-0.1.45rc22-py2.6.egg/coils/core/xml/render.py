#!/usr/bin/python
# Copyright (c) 2010 Adam Tauno Williams <awilliam@whitemice.org>
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
import logging, StringIO
from datetime import datetime, date
from xml.sax.saxutils import escape, unescape
from coils.core import *
import coils.core.omphalos

#TODO: Cleanup!  What a mess.
#TODO: Look at efficiency;  we are frequently doing several thousand of entities at a time


def describe_key_value(key, value):
    key = escape(key)
    if (value is None):
        return u'<{0}/>'.format(key)
    elif (isinstance(value, dict)):
        return u'<{0} dataType="complex">{1}</{0}>'.format(key, describe_dict(value))
    elif (isinstance(value, list)):
        return u'<{0} dataType="list">{1}</{0}>'.format(key, describe_list(value))
    else:
        return u'<{0}>{1}</{0}>'.format(key, escape(str(value)))


def describe_list(values):
    stream = StringIO.StringIO()
    for value in values:
        if (value is None):
            stream.write(u'<value/>'.format(key))
        elif (isinstance(value, dict)):
            stream.write(u'<value dataType="complex">{0}</value>'.format(describe_dict(value)))
        elif (isinstance(value, list)):
            stream.write(u'<value dataType="list">{0}</value>'.format(describe_list(value)))
        else:
            stream.write(u'<value>{0}</value>'.format(escape(str(value))))
    payload = stream.getvalue()
    stream.close()
    return payload


def describe_dict(collection):
    stream = StringIO.StringIO()
    for key in collection:
        key = escape(key)
        value = collection[key]
        if (value is None):
            stream.write(u'<{0}/>'.format(key))
        elif (isinstance(value, dict)):
            stream.write(u'<{0} dataType="complex">{1}</{0}>'.format(key, describe_dict(value)))
        elif (isinstance(value, list)):
            stream.write('<{0} dataType="list">{1}</{0}>'.format(key, describe_list(value)))
        else:
            stream.write(u'<{0}>{1}</{0}>'.format(key, escape(str(value))))
    payload = stream.getvalue()
    stream.close()
    return payload

def describe_type(value):
    if (isinstance(value, int)):
        return 'integer'
    if (isinstance(value, float)):
        return 'float'
    if (isinstance(value, str)):
        return 'string'
    if (isinstance(value, unicode)):
        return 'string'
    if (isinstance(value, list)):
        return 'list'
    if (isinstance(value, dict)):
        return 'complex'
    if (isinstance(value, datetime)):
        return 'datetime'
    if (isinstance(value, date)):
        return 'date'
    log = logging.getLogger('render')
    log.warn('Cannot describe data type: {0}'.format(type(value)))
    return 'unknown'


def describe_value(value):
    if (isinstance(value, int)):
        return str(value)
    if (isinstance(value, float)):
        return str(value)
    if (isinstance(value, str)):
        return escape(value)
    if (isinstance(value, unicode)):
        return escape(value)
    if (isinstance(value, datetime)):
        return value.strftime(u'%Y-%m-%dT%H:%M:%s')
    if (isinstance(value, date)):
        return value.strftime(u'%Y-%m-%d')
    if (isinstance(value, dict)):
        return describe_dict(value)
    if (isinstance(value, list)):
        return describe_list(value)
    log = logging.getLogger('render')
    log.warn('Cannot serialize data type: {0}'.format(type(value)))
    return ''

SUBMODE_DEFAULT      = 0
SUBMODE_COMPANYVALUE = 1
SUBMODE_CONTENTPLUGIN = 2
SUBMODE_TELEPHONE = 3
SUBMODE_ADDRESS = 4
SUBMODE_PROPERTY = 5
SUBMODE_FLAGS = 6

class Render(object):

    @staticmethod
    def render(entity, ctx, detailLevel=None, stream=None):
        if detailLevel is None: detailLevel = 65503
        if (stream is None):
            stream = StringIO.StringIO()
            result = True
        else:
            result = False
        stream.write(u'<?xml version="1.0" encoding="UTF-8"?>\n')
        if (isinstance(entity, list)):
            stream.write(u'<ResultSet>\n')
            for x in entity:
                stream.write(Render._render_entity(x, ctx, detailLevel=detailLevel))
                stream.write('\n')
                stream.flush()
            stream.write(u'</ResultSet>')
        else:
            stream.write(Render._render_entity(entity, ctx, detailLevel=detailLevel))
        if (result):
            data = stream.getvalue()
            stream.close()
        if (result):
            return data
        else:
            return None

    @staticmethod
    def _render_entity(entity, ctx):
        Render.render(entity, ctx, {})

    @staticmethod
    def _render_entity(entity, ctx, **params):
        log = logging.getLogger('render')
        data = None
        try:
            detail_level = params.get('detailLevel', 65503)
            omphalos = coils.core.omphalos.Render.Result(entity, detail_level, ctx)
            stream = StringIO.StringIO()
            stream.write(u'<entity entityName="{0}" objectId="{1}">'.\
                format(omphalos.get('entityName', 'Unknown'),
                       omphalos.get('objectId', 'na')))
            for key in omphalos:
                #if (key[0:1] == '_'):
                if (isinstance(omphalos[key], list)):
                    if (key == '_COMPANYVALUES'):
                        mode = SUBMODE_COMPANYVALUE
                        stream.write(u'<{0} mode="companyValue" dataType="list">'.format(key[1:].lower()));
                    elif (key == 'FLAGS'):
                        mode = SUBMODE_FLAGS
                        stream.write(u'<{0} mode="flags">'.format(key[1:].lower()));
                        # TODO: Implement flags mode
                    elif (key == '_PLUGINDATA'):
                        mode = SUBMODE_CONTENTPLUGIN
                        stream.write(u'<{0} mode="contentPlugin" dataType="list">'.format(key[1:].lower()));
                    elif (key == '_PHONES'):
                        mode = SUBMODE_TELEPHONE
                        stream.write(u'<{0} mode="telephone" dataType="list">'.format(key[1:].lower()));
                    elif (key == '_ADDRESSES'):
                        mode = SUBMODE_ADDRESS
                        stream.write(u'<{0} mode="address" dataType="list">'.format(key[1:].lower()));
                    else:
                        mode = SUBMODE_DEFAULT
                        stream.write(u'<{0} mode="default" dataType="list">'.format(key[1:].lower()));
                    for sub in omphalos[key]:
                        if (mode == SUBMODE_FLAGS):
                            pass
                        elif (mode == SUBMODE_COMPANYVALUE):
                            # Render CompanyValue
                            value = sub.get('value')
                            if (isinstance(value, list)):
                                stream.write(u'<companyvalue attribute="{0}" objectId="{1}"'
                                             u' label="{2}" uid="{3}" type="{4}" dataType="collection">'.\
                                    format(sub.get('attribute'),
                                           sub.get('objectId'),
                                           escape(sub.get('label')),
                                           sub.get('uid'),
                                           sub.get('type')))
                                for subvalue in value:
                                    stream.write(u'<value dataType="{0}">{1}</value>'.\
                                        format(describe_type(subvalue),
                                               describe_value(subvalue)))
                            else:
                                stream.write(u'<companyvalue attribute="{0}" objectId="{1}"'
                                             u' label="{2}" uid="{3}" type="{4}" dataType="{5}">'.\
                                    format(sub.get('attribute'),
                                           sub.get('objectId'),
                                           escape(sub.get('label')),
                                           sub.get('uid'),
                                           sub.get('type'),
                                           describe_type(value)))
                                stream.write(describe_value(sub.get('value')))
                            stream.write(u'</companyvalue>')
                        else:
                            # Use default subordinate render
                            if (mode == SUBMODE_CONTENTPLUGIN):
                                stream.write(u'<{0} contentPlugin="{1}" dataType="complex">'.\
                                    format(sub.get('entityName'),
                                           sub.get('pluginName')))
                            elif (mode == SUBMODE_ADDRESS) or (mode == SUBMODE_TELEPHONE):
                                stream.write(u'<{0} type="{1}" objectId="{2}" dataType="complex">'.\
                                    format(sub.get('entityName'),
                                           sub.get('type'),
                                           sub.get('objectId')))
                            elif ('objectId' in sub):
                                if ('targetObjectId' in sub):
                                    stream.write(u'<{0} objectId="{1}" targetObjectId="{2}" targetEntityName="{3}" dataType="complex">'.\
                                        format(sub.get('entityName'),
                                               sub.get('objectId'),
                                               sub.get('targetObjectId'),
                                               sub.get('targetEntityName')))
                                else:
                                    stream.write(u'<{0} objectId="{1}" dataType="complex">'.\
                                        format(sub.get('entityName'),
                                               sub.get('objectId')))
                            else:
                                log.debug('sub={0}'.format(sub))
                                subtype = sub.get('entityName', None)
                                if (subtype is None):
                                    log.error('Got a NULL entity name is subtype for objectId#{0} ({1})'.format(entity.object_id, entity.__entityName__))
                                stream.write(u'<{0} dataType="complex">'.\
                                    format(sub.get('entityName')))
                            for subkey in sub:
                                if (subkey in ('entityName', 'objectId')):
                                    continue
                                stream.write(u'<{0} dataType="{1}">{2}</{0}>'.\
                                    format(subkey,
                                           describe_type(sub[subkey]),
                                           describe_value(sub[subkey])))
                            stream.write(u'</{0}>'.format(sub.get('entityName')))

                    stream.write(u'</{0}>'.format(key[1:].lower()));
                else:
                    stream.write(u'<{0} dataType="{1}">{2}</{0}>'.\
                        format(key, describe_type(omphalos[key]), describe_value(omphalos[key])))
            stream.write(u'</entity>')
            omphalos = None
            data = stream.getvalue()
            stream.close()
            stream = None
        except Exception, e:
            log.exception(e)
            print e
        return data
