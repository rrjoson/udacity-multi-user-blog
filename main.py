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
import os
import re
import random
import hmac
import hashlib
import webapp2
import jinja2

from string import letters
from google.appengine.ext import db

# Jinja configuration

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)


# Global functions

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


# Handlers

class BlogHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class BlogFrontHandler(BlogHandler):

    def get(self):
        self.render('base.html')

class SignupHandler(BlogHandler):

    def get(self):
        self.render('signup.html')


# Routing

app = webapp2.WSGIApplication([
    ('/', BlogFrontHandler),
    ('/signup', SignupHandler)
], debug=True)
