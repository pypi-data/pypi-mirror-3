#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#
"""Starting template for Google App Engine applications.

Use this project as a starting point if you are just beginning to build a Google
App Engine project. Remember to fill in the OAuth 2.0 client_id and
client_secret which can be obtained from the Developer Console
<https://code.google.com/apis/console/>
"""

__author__ = 'jcgregorio@google.com (Joe Gregorio)'


import httplib2
import logging
import os
import pickle

from apiclient.discovery import build
from oauth2client.appengine import OAuth2Decorator
from oauth2client.client import AccessTokenRefreshError
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

# The client_id and client_secret are copied from the API Access tab on
# the Google APIs Console <http://code.google.com/apis/console>
decorator = OAuth2Decorator(
    client_id='837647042410-49mlotv28bfpn5a0igtinipsb8so5eob.apps.googleusercontent.com',
    client_secret='d4BSDjl4rmFmk-wh28_aK1Oz',
    scope='https://www.googleapis.com/auth/buzz')

http = httplib2.Http(memcache)
service = build("buzz", "v1", http=http)


class MainHandler(webapp.RequestHandler):

  @decorator.oauth_aware
  def get(self):
    path = os.path.join(os.path.dirname(__file__), 'grant.html')
    variables = {
        'url': decorator.authorize_url(),
        'has_credentials': decorator.has_credentials()
        }
    self.response.out.write(template.render(path, variables))


class FollowerHandler(webapp.RequestHandler):

  @decorator.oauth_required
  def get(self):
    try:
      http = decorator.http()
      followers = service.people().list(
          userId='@me', groupId='@followers').execute(http)
      text = 'Hello, you have %s followers!' % followers['totalResults']

      path = os.path.join(os.path.dirname(__file__), 'welcome.html')
      self.response.out.write(template.render(path, {'text': text }))
    except AccessTokenRefreshError:
      self.redirect('/')


def main():
  application = webapp.WSGIApplication(
      [
       ('/', MainHandler),
       ('/followers', FollowerHandler),
      ],
      debug=True)
  run_wsgi_app(application)


if __name__ == '__main__':
  main()
