#
#   Copyright 2011 Inkylabs et al.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# <Insert Marionetastical limerick here>
#
from .version import version_num

from http.client import HTTPConnection, HTTPSConnection
from json import dumps as json_dumps, loads as json_loads
from logging import getLogger
from mimetypes import guess_type
from os.path import exists as path_exists, join as path_join
from re import match as re_match
from sys import exc_info
from urllib.parse import urlencode
from urllib.request import urlopen


logger = getLogger(__name__)


def json_queryparams(qp):
    ret = {}
    for key, value in qp.items():
        ret[key] = value
        if not isinstance(value, str):
            ret[key] = json_dumps(value)
    return ret


def json_open(site, path, get=None, post=None, ssl=False):
    scheme = 'https' if ssl else 'http'
    url = '%s://%s/%s' % (scheme, site, path)
    if get != None:
        url += '?' + urlencode(json_queryparams(get))
    kwargs = {}
    if post != None:
        kwargs['data'] = urlencode(json_queryparams(post)).encode()
    logger.info('visiting ' + url)
    response = urlopen(url, **kwargs)
    return json_loads(response.read().decode())


def post_multipart(url, data):
    # Encode the data
    boundary = '----------nhaeohnjuobn'
    lines = []
    for key, value in data.items():
        lines.append('--' + boundary)
        lines.append('Content-Disposition: form-data; name="%s"' % key)
        if hasattr(value, 'read'):
            lines[-1] += '; filename="%s"' % value.name
            content_type = guess_type(value.name)[0] or 'application/octet-stream'
            lines.append('Content-Type: %s' % content_type)
            value = value.read()
        lines.append('')
        lines.append(str(value))
    lines.append('--' + boundary + '--')
    lines.append('')
    body = '\r\n'.join(lines)
    content_type = 'multipart/form-data; boundary=%s' % boundary

    # Send the request
    url_match = re_match('http(s)?://(.*?)(/.*)', url)
    conn_type = HTTPSConnection if url_match.group(1) else HTTPConnection
    connection = conn_type(url_match.group(2))
    connection.request('POST', url_match.group(3), body,
                       headers={'content-type': content_type})
    return connection.getresponse()


class RequestError(Exception):
    pass


class InvalidKeyError(RequestError):
    pass


class UserClient:
    def __init__(self, site, ssl=True):
        self.site = site
        self.ssl = ssl

    def request(self, path, get=None, post=None):
        data = json_open(self.site, path, get, post, self.ssl)
        for error in data.get('errors', []):
            if 'Invalid worker key' in error:
                raise InvalidKeyError(error)
            raise RequestError(error)
        return data

    def batch_request(self, path, get={}, post=None, fields=[], batch_size=10):
        if not post or not fields:
            return
        start = 0
        while True:
            to_post = {}
            to_post.update(post)
            for field in fields:
                to_post[field] = to_post[field][start:batch_size]
                if not to_post[field]:
                    return
            self.request(path, get, to_post)
            start += batch_size

    def get_config(self, uid):
        return self.request('users/%d.json' % uid)

    def get_min_user_version(self):
        return self.request('_version')['min_user_version']


class ClusterClient(UserClient):
    def __init__(self, site, key, ssl=True, version=version_num):
        super(ClusterClient, self).__init__(site, ssl)
        self.base_get = {
            'key': key,
            'version': version
        }

    def request(self, path, get={}, post=None):
        to_get = {}
        to_get.update(self.base_get)
        to_get.update(get)
        data = super(ClusterClient, self).request(path, to_get, post)
        return data

    def fetch_players(self):
        return self.request('fetch_players')['player_configs']

    def delete_players(self, uids):
        self.batch_request('delete_users', post={'player_ids': uids},
                           fields=['player_ids'])

    def flag_players(self, uids):
        self.batch_request('flag_users', post={'player_ids': uids},
                           fields=['player_ids'])

    def report_results(self, results):
        self.batch_request('report_results', post={'results': results},
                           fields=['results'])

    def upload_replay(self, players, replay_dir):
        data = self.request('create_replay',
                            post={'users': [player.uid for player in players]})
        limit = 0
        while path_exists(path_join(replay_dir, str(limit))):
            limit += 1
        replay = data['id']
        for i in range(limit):
            f = open(path_join(replay_dir, str(i)))
            post_params = {
                'replay': replay,
                'pos': str(i),
                'final': '1' if i == limit - 1 else '0',
                'file': f,
            }
            post_params.update(data['upload_data'])
            response = post_multipart(data['upload_url'], data=post_params)
            response = urlopen(response.getheader('Location'))
            data = json_loads(response.read().decode())
            i += 1
