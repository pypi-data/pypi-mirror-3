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
from http.server import SimpleHTTPRequestHandler
from imp import find_module
from os import getcwd
from os.path import abspath, join as path_join
from socket import error as socket_error
from socketserver import TCPServer
from threading import Thread
from time import sleep
from urllib.request import urlopen
from urllib.error import URLError


def create_ReplayHTTPRequestHandler(replay_dir):
    # Set up the symlinks
    cwd = getcwd()
    mod_dir = find_module('marionette')[1]
    media_dir = path_join(mod_dir, 'replay', 'web')
    replace_prefix = [
        (path_join(cwd, 'replay', ''), path_join(abspath(replay_dir), '')),
        (cwd, media_dir),
    ]

    # Create the handler
    class Handler(SimpleHTTPRequestHandler):
        def translate_path(self, path):
            translated = super(Handler, self).translate_path(path)
            for match, sub in replace_prefix:
                if translated.startswith(match):
                    return translated.replace(match, sub, 1)
            return translated

    return Handler


class ReplayServerThread(Thread):
    def __init__(self, replay_dir, *args, **kwargs):
        self.replay_dir = replay_dir
        super(ReplayServerThread, self).__init__(*args, **kwargs)
        self.daemon = True
        self.port = 9001

    def run(self):
        Handler = create_ReplayHTTPRequestHandler(self.replay_dir)
        class ReusableTCPServer(TCPServer):
            allow_reuse_address = True
        # TODO: Serve quietly
        while True:
            try:
                httpd = ReusableTCPServer(('', self.port), Handler)
                break
            except socket_error as e:
                if e.errno != 98:
                    raise e
                self.port += 1
        httpd.serve_forever()


class ReplayServer(object):

    """
    This class manages a thread that has a server using a subclass of
    python's SimpleHTTPRequestHandler.
    SimpleHTTPRequestHandler usually serves a directory but we want
    to emulate doing this with a directory of symlinks to the replay, js, img,
    etc. directories.

    """

    def __init__(self, replay_dir):
        self.thread = ReplayServerThread(replay_dir)

    def start(self):
        self.thread.start()
        while True:
            url = 'http://localhost:%d/' % self.thread.port
            try:
                urlopen(url, timeout=.1)
            except URLError:
                sleep(.1)
                continue
            break
        return self.thread.port

    def stop(self):
        self.thread.join(0)

    def wait(self):
        while True:
            sleep(1)
