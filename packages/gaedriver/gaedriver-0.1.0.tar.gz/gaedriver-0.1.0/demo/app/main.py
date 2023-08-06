#!/usr/bin/env python
#
# Copyright 2011 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Demo application for gaedriver."""

__author__ = 'schuppe@google.com (Robert Schuppenies)'

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util


class DefaultRequestHandler(webapp.RequestHandler):

  # lower case method name required by API - pylint: disable-msg=C6409
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.response.out.write('Hello World')


application = webapp.WSGIApplication([
    ('.*', DefaultRequestHandler)
    ])


def main():
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
