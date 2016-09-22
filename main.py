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


# Validation

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

def valid_username(username):
    return username and USER_RE.match(username)

def valid_password(password):
    return password and PASS_RE.match(password)

def valid_email(email):
    return not email or EMAIL_RE.match(email)


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

    def post(self):
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

        if not valid_username(self.username):
            params['error'] = "That's not a valid username."
            return self.render('signup.html', **params)

        if not valid_password(self.password):
            params['error'] = "That wasn't a valid password."
            return self.render('signup.html', **params)

        elif self.password != self.verify:
            params['error'] = "Your passwords didn't match."
            return self.render('signup.html', **params)

        if not valid_email(self.email):
            params['error'] = "That's not a valid email."
            return self.render('signup.html', **params)

        self.write("Welcome!")


class LoginHandler(BlogHandler):

    def get(self):
        self.render('login.html')


# Routing

app = webapp2.WSGIApplication([
    ('/', BlogFrontHandler),
    ('/signup', SignupHandler),
    ('/login', LoginHandler),
], debug=True)
