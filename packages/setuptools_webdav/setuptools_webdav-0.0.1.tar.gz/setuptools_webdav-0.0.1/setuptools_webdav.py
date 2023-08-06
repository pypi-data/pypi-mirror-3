'''
Copyright 2012 Marian Neagul <mneagul@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

@author: Marian Neagul
@contact: mneagul@gmail.com
@copyright: 2012 Marian Neagul <mneagul@gmail.com>
'''

import os
import ConfigParser

from distutils.errors import DistutilsOptionError
from distutils import log
from setuptools import Command
from webdav import WebdavClient

class webdav_upload(Command):
    description = "upload package to a webdav server"
    user_options = [
        ("repository=", "r", "URL of repository"),
        ]

    def initialize_options(self):
        self.username = ''
        self.password = ''
        self.repository = ''
        self.resource = None

    def finalize_options(self):
        if os.environ.has_key('HOME'):
            rc = os.path.join(os.environ['HOME'], '.pypirc')
            if os.path.exists(rc):
                self.announce('Using login from %s' % rc)
                config = ConfigParser.ConfigParser({
                        'username':'',
                        'password':'',
                        'repository':''})
                config.read(rc)

                if not self.repository:
                    self.repository = config.get('webdav', 'repository')
                if not self.username:
                    self.username = config.get('webdav', 'username')
                if not self.password:
                    self.password = config.get('webdav', 'password')
        if not self.repository:
            raise DistutilsOptionError("No repository specified !")

        self.announce("Uploading to repository: %s" % (self.repository,), level = log.INFO)
        self.resource = WebdavClient.CollectionStorer(self.repository)
        if self.username:
            self.resource.connection.addBasicAuthorization(self.username, self.password)

    def run(self):
        if not self.distribution.dist_files:
            raise DistutilsOptionError("No dist file created in earlier command")

        for distribution, python_version, filename in self.distribution.dist_files:
            self.webdav_upload(distribution, python_version, filename)

    def webdav_upload(self, distribution, python_version, filename):
        destination_file = os.path.basename(filename)
        self.announce("Uploading %s" % (destination_file,), level = log.INFO)
        child = self.resource.addResource(destination_file)
        child.uploadFile(open(filename, "rb"))
