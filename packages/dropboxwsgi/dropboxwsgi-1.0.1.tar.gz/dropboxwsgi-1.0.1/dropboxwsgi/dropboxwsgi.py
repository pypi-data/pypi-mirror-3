#!/usr/bin/python
#
# This file is part of dropboxwsgi.
#
# Copyright (c) Dropbox, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

from __future__ import absolute_import

import calendar
import errno
import logging
import os
import pprint
import sys
import tempfile
import time
import traceback
import urllib

try:
    import json
except Exception:
    import simplejson as json

from cgi import parse_qs
from wsgiref.simple_server import make_server
from wsgiref.validate import validator

import dropbox

from dropbox.rest import ErrorResponse

from .six import b, r
from ._version import __version__

# TODO: Range Requests (need to extend Dropbox SDK)
# TODO: HEAD/PUT/POST Requests
# TODO: Support index.html-like files

logger = logging.getLogger(__name__)

def tz_offset(tz_string):
    factor = 1 if tz_string[0] == '+' else -1
    hours = 3600 * int(tz_string[1:3])
    minutes = 60 * int(tz_string[3:5])
    return factor * (hours + minutes)

def dropbox_date_to_posix(date_string):
    fmt_date, tz = date_string.rsplit(' ', 1)
    ts = calendar.timegm(time.strptime(fmt_date, "%a, %d %b %Y %H:%M:%S"))
    return ts + tz_offset(tz)

def posix_to_http_date(ts=None):
    if ts is None:
        ts = time.time()
    HTTP_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"
    return time.strftime(HTTP_DATE_FORMAT, time.gmtime(ts))

def http_date_to_posix(date_string):
    # parse date string in three different formats
    # 1) Sun, 06 Nov 1994 08:49:37 GMT  ; RFC 822, updated by RFC 1123
    # 2) Sunday, 06-Nov-94 08:49:37 GMT ; RFC 850, obsoleted by RFC 1036
    # 3) Sun Nov  6 08:49:37 1994       ; ANSI C's asctime() format
    for fmt in ["%a, %d %b %Y %H:%M:%S GMT",
                "%A, %d-%b-%y %H:%M:%S GMT",
                "%a %b %d %H:%M:%S %Y"]:
        try:
            _tt = time.strptime(date_string, fmt)
        except ValueError:
            continue
        return calendar.timegm(_tt)
    else:
        raise ValueError("Date could not be parsed")

MATCH_ANY = object()
def get_match(environ, key_name):
    try:
        if_none_match = environ[key_name]
    except KeyError:
        return None
    else:
        if if_none_match.strip() == "*":
            return MATCH_ANY
        else:
            return [a.strip() for a in if_none_match.split(',')]

# it's nice to have this as a separate function
HTTP_PRECONDITION_FAILED = 412
HTTP_NOT_MODIFIED = 304
HTTP_OK = 200
def http_cache_logic(current_etag, current_modified_date,
                     if_match, if_none_match, last_modified_since):
    logger.debug("current_etag: %r", current_etag)
    logger.debug("current_modified_date: %r", current_modified_date)
    logger.debug("if_match: %r", if_match)
    logger.debug("if_none_match: %r", if_none_match)
    logger.debug("last_modified_since: %r", last_modified_since)

    if (if_match is not None and
        not (if_match is MATCH_ANY or
             any(e == current_etag for e in if_match))):
        logger.debug("precondition failed")
        return HTTP_PRECONDITION_FAILED

    if ((if_none_match is not None and
         (if_none_match is MATCH_ANY or
          any(e == current_etag for e in if_none_match)) and
         (last_modified_since is None or
          current_modified_date is None or
          current_modified_date <= last_modified_since)) or
        # this logic sucks, this is the case where if_none_match is not specified
        (if_none_match is None and
         last_modified_since is not None and
         current_modified_date is not None and
         current_modified_date <= last_modified_since)):
        logger.debug("not modified")
        return HTTP_NOT_MODIFIED

    logger.debug("return ok")
    return HTTP_OK

class FileSystemCredStorage(object):
    def __init__(self, app_dir):
        self.access_token_path = os.path.join(app_dir, 'access_token')

    def read_access_token(self):
        # TODO: check validity of data stored in file
        # and blow away if invalid
        with open(self.access_token_path, 'r') as f:
            return json.load(f)

    def write_access_token(self, key, secret):
        with open(self.access_token_path, 'w') as f:
            json.dump((key, secret), f)

class MemoryCredStorage(object):
    def __init__(self):
        self._token = None

    def read_access_token(self):
        if self._token is None:
            raise Exception("No Token!")
        return self._token

    def write_access_token(self, key, secret):
        self._token = (key, secret)

def _make_server_tag(environ):
    ss = environ.get('SERVER_SOFTWARE', '')
    if ss:
        ss = ' ' + ss

    return ('dropboxwsgi/%(version)s%(server_software)s' %
            dict(version=__version__, server_software=ss))

def _render_directory_contents(environ, md):
    # TODO: a version for mobile devices would be nice
    ret_path = md['path']
    yield (u'''<!DOCTYPE html>
<html>
<head>
<title>Index of %(path)s%(trail)s</title>
<style type="text/css">
a, a:active {text-decoration: none; color: blue;}
a:visited {color: #48468F;}
a:hover, a:focus {text-decoration: underline; color: red;}
body {background-color: #F5F5F5;}
table {margin-left: 12px;}
h1 { font-size: -1;}
th, td { font: 90%% monospace; text-align: left;}
th { font-weight: bold; padding-right: 14px; padding-bottom: 3px;}
td {padding-right: 14px;}
td.s, th.s {text-align: right;}
div.list { background-color: white; border-top: 1px solid #646464; border-bottom: 1px solid #646464; padding-top: 10px; padding-bottom: 14px;}
div.foot { font: 90%% monospace; color: #787878; padding-top: 4px;}
</style>
</head>
<body>
<h1>Index of %(path)s%(trail)s</h1>
<div class="list">
<table summary="Directory Listing" cellpadding="0" cellspacing="0">
<thead>
<tr>
<th class="n">Name</th>
<th class="m">Last Modified</th>
<th class="s">Size</th>
<th class="t">Type</th>
</tr>
</thead>
<tbody>
''' % dict(path=ret_path, trail=u"" if ret_path[-1] == u"/" else u"/")).encode('utf-8')

    if md['path'] != u'/':
        yield b('<tr>\n')
        yield b('<td class="n"><a href="../">Parent Directory</a>/</td>\n')
        yield b('<td class="m"></td>\n')
        yield b('<td class="s">-&nbsp;&nbsp;</td>\n')
        yield b('<td class="t">Directory</td>\n')
        yield b('</tr>\n')

    # Show directories first
    md['contents'].sort(key=lambda ent: (not ent['is_dir'], ent['path']))
    for entry in md['contents']:
        path = entry['path']
        name = path.rsplit(u'/', 1)[1]
        trail = u"/" if entry['is_dir'] else u""
        yield b('<tr>\n')
        yield (u'<td class="n"><a href="%s%s">%s</a>%s</td>\n'
               % (name, trail, name, trail)).encode('utf8')
        yield (u'<td class="m">%s</td>\n'
               % time.strftime(u"%Y-%b-%d %H:%M:%S", time.gmtime(dropbox_date_to_posix(r(entry['modified']))))).encode('utf8')
        yield (u'<td class="s">%s</td>\n'
               % (u'- &nbsp;'
                  if entry['is_dir'] else
                  entry['size'])).encode('utf8')
        yield (u'<td class="t">%s</td>\n'
               % (u'Directory' if entry['is_dir'] else entry['mime_type'])).encode('utf8')
        yield b('</tr>\n')

    toyield = ('''</tbody>
</table>
</div>
<div class="foot">%s</div>
</body>
</html>''' % _make_server_tag(environ))

    if sys.version_info >= (3,):
        toyield = toyield.encode('utf8')

    yield toyield

def make_app(config, impl):
    http_root = config['http_root']
    finish_link_path = '/finish_link'
    block_size = 16 * 1024
    allow_directory_listing = config.get('allow_directory_listing', True)

    index_file_list = config.get('index_file_names')
    if index_file_list:
        index_files = set(a.lower() for a in index_file_list)
        def finder_(directory_contents):
            for ent in directory_contents:
                if (ent['path'].rsplit(u'/', 1)[1].lower() in index_files and
                    not ent['is_dir']):
                    return ent['path']
        find_index_file = finder_
    else:
        find_index_file = None

    sess = dropbox.session.DropboxSession(config['consumer_key'],
                                          config['consumer_secret'],
                                          config['access_type'])

    # get token
    try:
        at = impl.read_access_token()
    except Exception:
        # TODO check exception type
        traceback.print_exc()
    else:
        sess.set_token(*at)

    client = dropbox.client.DropboxClient(sess)

    def link_app(environ, start_response):
        # this is the pingback
        if environ['PATH_INFO'] == finish_link_path:
            query_args = parse_qs(environ['QUERY_STRING'])

            oauth_token = query_args['oauth_token'][0]
            if oauth_token != sess.request_token.key:
                raise Exception("Non-matching request token")

            try:
                at = sess.obtain_access_token()
            except Exception:
                # request token was bad, link again
                sess.request_token = None
            else:
                impl.write_access_token(at.key, at.secret)
                start_response('200 OK', [('Content-type', 'text/plain')])
                return ['Server is now Linked! Browse at will']

        # check if we have a request_token lying around already
        if not sess.request_token:
            sess.obtain_request_token()

        auth_url = sess.build_authorize_url(sess.request_token,
                                            http_root + finish_link_path)
        start_response('302 FOUND', [('Content-type', 'text/plain'),
                                     ('Location', auth_url)])
        return ['Redirecting...']

    def not_found_response(environ, start_response):
        start_response('404 NOT FOUND', [('Content-type', 'text/plain')])
        return [b('Not Found!')]

    def bad_gateway_response(environ, start_response):
        start_response('502 BAD GATEWAY', [('Content-type', 'text/plain')])
        return [b('Bad Gateway!')]

    def not_modified_response(environ, start_response):
        start_response('304 NOT MODIFIED', [])
        return []

    def precondition_failed_response(environ, start_response):
        start_response('412 PRECONDITION FAILED', [('Content-type', 'text/plain')])
        return [b('Precondition Failed!')]

    def add_server_tag(app):
        def new_app(environ, start_response):
            def my_start_response(code, headers):
                headers.append(('Server', _make_server_tag(environ)))
                return start_response(code, headers)
            return app(environ, my_start_response)
        return new_app

    @add_server_tag
    def app(environ, start_response):
        # TODO: support other request methods
        if environ['REQUEST_METHOD'].upper() != 'GET':
            start_response('405 METHOD NOT ALLOWED', [('Content-type', 'text/plain'),
                                                      ('Allow', 'GET')])
            return [b('Method Not Allowed!')]

        # checked if we are linked yet
        if not sess.is_linked():
            return link_app(environ, start_response)

        path = environ['PATH_INFO']

        if sys.version_info >= (3,):
            path = path.encode('latin1')

        # turn path into unicode
        for enc in ['utf8', 'latin1']:
            try:
                path = path.decode(enc)
            except UnicodeDecodeError:
                pass
            else:
                break
        else:
            return not_found_response(environ, start_response)

        if_match = get_match(environ, 'HTTP_IF_MATCH')
        if_none_match = get_match(environ, 'HTTP_IF_NONE_MATCH')

        # generate the kw args for metadata()
        # based on the passed in etag
        if (if_none_match is not None and
            if_none_match is not MATCH_ANY and
            len(if_none_match) == 1 and
            if_none_match[0].startswith('"d') and
            # don't want to eager 304 if we're going to look
            # through the contents
            not find_index_file):
            kw = {'hash' : if_none_match[0][2:-1]}
        else:
            kw = {}

        should_list = (path[-1] == u"/" and
                       (find_index_file or
                        allow_directory_listing))

        try:
            md = client.metadata(path, list=should_list, **kw)
        except Exception, e:
            if (isinstance(e, ErrorResponse) and
                (e.status in (304, 404))):
                if e.status == 304:
                    return not_modified_response(environ, start_response)
                elif e.status == 404:
                    logging.debug("API error says not found: %r", path)
                    return not_found_response(environ, start_response)
            else:
                logger.exception("API Error")
                return bad_gateway_response(environ, start_response)

        if md.get('is_deleted'):
            # if the file is deleted just cancel early
            logging.debug("File is deleted: %r", path)
            return not_found_response(environ, start_response)

        if md['is_dir'] and path[-1] != u"/":
            start_response('307 Temporary Redirect',
                           [('Location', '%s%s/' % (http_root, urllib.quote(r(path, enc='utf8')))),
                            # wsgiref.validator fails if we don't include this
                            ('Content-Type', 'text/plain')])
            return []

        # Handle index files
        if md['is_dir'] and find_index_file:
            index_file = find_index_file(md['contents'])
            if index_file is not None:
                try:
                    md2 = client.metadata(index_file, list=False)
                except Exception:
                    logger.exception("Exception while trying to get index file")
                else:
                    print md2
                    # make sure this index file didn't turn into a directory
                    # in the interim
                    if not md2['is_dir'] and not md2.get('is_deleted'):
                        path = index_file
                        md = md2

        if md['is_dir']:
            if not allow_directory_listing:
                # if we're not allowing directory listings
                # just exit early
                start_response('403 FORBIDDEN', [('Content-type', 'text/plain')])
                return [b('Forbidden')]

            current_etag = r(u'"d%s"' % md['hash'])
            # we don't set a modified date for directories
            # because md['modified'] applies to the directory entry
            # itself in the dropbox api, not addition or removal of children
            # we could use include_deleted and use max(ent['modified']) of all
            # children but the 10000 entry limit scares me when including deleted files
            current_modified_date = None
            def directory_response(environ, start_response):
                start_response('200 OK', [('Content-type', 'text/html; charset=utf-8'),
                                          ('Cache-Control', 'public, no-cache'),
                                          ('ETag', current_etag)])
                return _render_directory_contents(environ, md)

            toret = directory_response
        else:
            current_etag = r(u'"_%s"' % md['rev'])
            current_modified_date = dropbox_date_to_posix(r(md['modified']))
            def file_response(environ, start_response):
                last_modified_date = posix_to_http_date(current_modified_date)
                start_response('200 OK', [('Content-Type', r(md['mime_type'])),
                                          ('Cache-Control', 'public, no-cache'),
                                          ('Content-Length', str(md['bytes'])),
                                          ('ETag', current_etag),
                                          ('Last-Modified', last_modified_date)])

                res = client.get_file(path, rev=md['rev'])
                def gen():
                    try:
                        while True:
                            ret = res.read(block_size)
                            if not ret:
                                break
                            yield ret
                    finally:
                        res.close()

                return gen()

            toret = file_response

        try:
            if_modified_since = environ['HTTP_IF_MODIFIED_SINCE']
        except KeyError:
            if_modified_since = None
        else:
            if_modified_since = http_date_to_posix(if_modified_since)

        return_code = http_cache_logic(current_etag, current_modified_date,
                                       if_match, if_none_match, if_modified_since)

        if return_code == HTTP_PRECONDITION_FAILED:
            return precondition_failed_response(environ, start_response)
        elif return_code == HTTP_NOT_MODIFIED:
            return not_modified_response(environ, start_response)
        else:
            return toret(environ, start_response)

    return app

if __name__ == "__main__":
    config = dict(consumer_key='iodc7pv1hlolg5a',
                  consumer_secret='bqynhr0h1ivucm5',
                  access_type='app_folder',
                  allow_directory_listing=True,
                  http_root='http://localhost:8080',
                  app_dir=os.path.expanduser('~/.dropboxhttp'))

    logging.basicConfig(level=logging.DEBUG)
    impl = FileSystemCredStorage(config['app_dir'])
    make_server('', 8080, validator(make_app(config, impl))).serve_forever()
