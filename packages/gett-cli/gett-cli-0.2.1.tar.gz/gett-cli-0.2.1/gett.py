# Copyright 2011 - Mickaël THOMAS

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import pprint
import datetime
import threading
import os.path

from urllib.request import urlopen, Request
from urllib.parse import urlencode
from urllib.error import HTTPError
from urllib.parse import urlparse

from http.client import HTTPConnection

API_BASE = 'https://open.ge.tt/1/'
API_KEY = 't05kormjprb2o6rm8f8wmts2thjjor'
DEBUG = False

class APIError(Exception):
    pass

def _post_request(path, **kwargs):
    qskeys = {}
    url = API_BASE + path

    for key, value in list(kwargs.items()):
        if key.startswith('_'):
            qskeys[key[1:]] = value
            del kwargs[key]

    if qskeys:
        url += '?' + urlencode(qskeys)

    input_data = json.dumps(kwargs).encode('utf-8')
    request = Request(url, input_data)

    return _request(request)

def _get_request(path, **kwargs):
    url = API_BASE + path

    if kwargs:
        url += '?' + urlencode(kwargs)

    request = Request(url)
    return _request(request)

def _request(req):
    if DEBUG:
        print('--------------------------------------------------------------------------------')
        print("%s request to %s -->" % (req.get_method(), req.full_url))

        if req.data:
            print('data: ' + req.data.decode('utf-8'))

    try:
        resp = urlopen(req)
        raw = resp.read()
    except HTTPError as ex:
        resp = ex
        raw = ex.read()

    raw = raw.decode('utf-8')

    try:
        result = json.loads(raw)
    except:
        print('Error: unable to decode JSON: %s' % raw)
        raise

    if DEBUG:
        print('response (%d):' % resp.status)

        pprint.pprint(result)
        print()

    if "error" in result:
        raise APIError(result["error"])

    return result

class User(object):
    def _load(self, result):
        self.atoken = result['accesstoken']
        self.rtoken = result['refreshtoken']
        self.userid = result['user']['userid']
        self.email = result['user']['email']
        self.full_name = result['user']['fullname']
        self.storage_used = result['user']['storage']['used']
        self.storage_limit = result['user']['storage']['limit']

    def refresh(self):
        self.login_token(self.rtoken)

    def login_auth(self, email, password):
        result = _post_request('users/login', apikey=API_KEY, email=email, password=password)
        self._load(result)

    def login_token(self, rtoken):
        result = _post_request('users/login', refreshtoken=rtoken)
        self._load(result)

    def list_shares(self, skip=None, limit=None):
        if skip is not None and limit is not None:
            results = _get_request('shares', accesstoken=self.atoken, skip=str(skip), limit=str(limit))
        else:
            results = _get_request('shares', accesstoken=self.atoken)

        for share_result in results:
             share = UserShare(self)
             share._load(share_result)
             yield share

    def get_share(self, name):
        result = _get_request('shares/' + name)

        share = UserShare(self)
        share._load(result)

        return share

    def create_share(self, title=None):
        if title is not None:
            result = _post_request('shares/create', _accesstoken=self.atoken, title=title)
        else:
            result = _post_request('shares/create', _accesstoken=self.atoken)

        share = UserShare(self)
        share._load(result)

        return share

class Share(object):
    def __init__(self, name):
        self.name = name
        self.refresh()

    def _load(self, result):
        self.name = result['sharename']
        self.title = result.get('title')
        self.created = datetime.datetime.fromtimestamp(result['created'])
        self.url = result.get('getturl')
        self.files = {}

        # FIXME: work around API omission
        if not self.url:
            self.url = 'http://ge.tt/%s' % self.name

        for file_result in result['files']:
            f = File(self)
            f._load(file_result)

            self.files[f.id] = f

    def refresh(self):
        result = _get_request('shares/' + self.name)
        self._load(result)

class UserShare(Share):
    def __init__(self, user):
        self.user = user

    def update(self, **fields):
        result = _post_request('shares/%s/update' % self.name, _accesstoken=self.user.atoken, **fields)
        self._load(result)

    def destroy(self):
        _post_request('shares/%s/destroy' % self.name, _accesstoken=self.user.atoken)

    def create_file(self, filename, size=None):
        result = _post_request('files/%s/create' % self.name, _accesstoken=self.user.atoken, filename=filename)
        file = File(self)
        file._load(result)
        file.size = size
        self.files[file.id] = file
        return file

class File(object):
    def __init__(self, share):
        self.share = share

    def _load(self, result):
        self.name = result['filename']
        self.id = result['fileid']
        self.size = result.get('size')
        self.downloads = result['downloads']
        self.readystate = result['readystate']
        self.created = datetime.datetime.fromtimestamp(result['created'])
        self.url = result.get('getturl')

        # FIXME: work around API omission
        if not self.url:
            self.url = self.share.url + '/v/%s' % self.id

        if 'upload' in result:
            self.put_url = result['upload']['puturl']
        else:
            self.put_url = None

    def destroy(self):
        _post_request('files/%s/%s/destroy' % (self.share.name, self.id), _accesstoken=self.share.user.atoken)
        del self.share.files[self.id]

    def refresh(self):
        result = _get_request('files/%s/%s' % (self.share.name,  self.id))
        self._load(result)

class FileUpload(threading.Thread):
    def __init__(self, file, fp):
        super().__init__()

        self.file = file
        self.fp = fp
        self.file_size = file.size
        self.percent_done = 0
        self.bytes_written = 0
        self.ex = None

    def run(self):
        try:
            parsed = urlparse(self.file.put_url)
            conn = HTTPConnection(parsed.netloc)
            conn.connect()
            conn.putrequest('PUT', parsed.path + (('?' + parsed.query) if parsed.query else ''))
            conn.putheader('Content-Length', str(self.file_size))
            conn.endheaders()

            while self.bytes_written != self.file_size:
                data = self.fp.read(4096)
                conn.sock.sendall(data)
                self.bytes_written += len(data)
                self.percent_done = self.bytes_written * 100 / self.file_size

            self.percent_done = 100 # needed when file_size is zero...

            resp = conn.getresponse()
        except Exception as ex:
            self.ex = ex
