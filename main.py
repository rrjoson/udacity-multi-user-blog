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

import webapp2

from helpers import *
from google.appengine.ext import db

# Models
from models.user import User
from models.post import Post
from models.like import Like
from models.comment import Comment

# Handlers
from handlers.blog import BlogHandler


class BlogFrontHandler(BlogHandler):

    def get(self):
        posts = db.GqlQuery(
            "select * from Post order by created desc limit 10")

        self.render('front.html', posts=posts)

class SignupHandler(BlogHandler):

    def done(self):
        u = User.by_name(self.username)

        if u:
            error = 'That user already exists.'
            self.render('signup.html', error=error)

        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')

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

        self.done()

class LoginHandler(BlogHandler):

    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)

        if u:
            self.login(u)
            self.redirect('/')
        else:
            error = 'Invalid Username or Password'
            self.render('login.html', error=error)

class LogoutHandler(BlogHandler):

    def get(self):
        self.logout()
        self.redirect('/')

class PostHandler(BlogHandler):

    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        comments = db.GqlQuery(
            "select * from Comment where ancestor is :1 order by created desc limit 10", key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post=post, comments=comments)

class NewPostHandler(BlogHandler):

    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            error = "You must be signed in to create a post."
            self.render("base.html", access_error=error)

    def post(self):
        if not self.user:
            return self.redirect('/login')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent=blog_key(), subject=subject,
                     content=content, user_id=self.user.key().id())
            p.put()
            self.redirect('/%s' % str(p.key().id()))
        else:
            error = "Please fill up the fields."
            self.render("newpost.html", subject=subject,
                        content=content, error=error)

class EditPostHandler(BlogHandler):

    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if self.user and self.user.key().id() == post.user_id:
            self.render('editpost.html', subject=post.subject,
                        content=post.content, post_id=post_id)

        elif not self.user:
            self.redirect('/login')

        else:
            self.write("You cannot edit this post becuase you are not the one who wrote this post.")

    def post(self, post_id):
        if not self.user:
            return self.redirect('/login')

        if self.user and self.user.key().id() == post.user_id:    
            subject = self.request.get('subject')
            content = self.request.get('content')

            if subject and content:
                key = db.Key.from_path('Post', int(post_id), parent=blog_key())
                post = db.get(key)

                post.subject = subject
                post.content = content

                post.put()

                self.redirect('/%s' % str(post.key().id()))
            else:
                error = "subject and content, please!"
                self.render("newpost.html", subject=subject,
                            content=content, error=error)

        else:
            self.write("You cannot edit this post becuase you are not the one who wrote this post.")

class DeletePostHandler(BlogHandler):

    def get(self, post_id, post_user_id):
        if self.user and self.user.key().id() == int(post_user_id):
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            post.delete()

            self.redirect('/')

        elif not self.user:
            self.redirect('/login')

        else:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            comments = db.GqlQuery(
                "select * from Comment where ancestor is :1 order by created desc limit 10", key)

            error = "You don't have permission to delete this post"
            self.render("permalink.html", post=post, comments=comments, error=error)

class LikePostHandler(BlogHandler):

    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if self.user and self.user.key().id() == post.user_id:
            error = "Sorry, you cannot like your own post."
            self.render('base.html', access_error=error)
        elif not self.user:
            self.redirect('/login')
        else:
            user_id = self.user.key().id()
            post_id = post.key().id()

            like = Like.all().filter('user_id =', user_id).filter('post_id =', post_id).get()

            if like:
                self.redirect('/' + str(post.key().id()))

            else:
                like = Like(parent=key, 
                            user_id=self.user.key().id(),
                            post_id=post.key().id())

                post.likes += 1

                like.put()
                post.put()

                self.redirect('/' + str(post.key().id()))

class UnlikePostHandler(BlogHandler):

    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if self.user and self.user.key().id() == post.user_id:
            self.write("You cannot dislike your own post")
        elif not self.user:
            self.redirect('/login')
        else:
            user_id = self.user.key().id()
            post_id = post.key().id()

            l = Like.all().filter('user_id =', user_id).filter('post_id =', post_id).get()

            if l:
                l.delete()
                post.likes -= 1
                post.put()

                self.redirect('/' + str(post.key().id()))
            else:
                self.redirect('/' + str(post.key().id()))

class AddCommentHandler(BlogHandler):

    def get(self, post_id, user_id):
        if not self.user:
            self.render('/login')
        else:
            self.render("addcomment.html")

    def post(self, post_id, user_id):
        if not self.user:
            return

        content = self.request.get('content')

        user_name = self.user.name
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())

        c = Comment(parent=key, user_id=int(user_id), content=content, user_name=user_name)
        c.put()

        self.redirect('/' + post_id)

class EditCommentHandler(BlogHandler):

    def get(self, post_id, post_user_id, comment_id):
        if self.user and self.user.key().id() == int(post_user_id):
            postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
            key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
            comment = db.get(key)

            self.render('editcomment.html', content=comment.content)

        elif not self.user:
            self.redirect('/login')

        else:
            self.write("You don't have permission to edit this comment.")

    def post(self, post_id, post_user_id, comment_id):
        if not self.user:
            return

        if self.user and self.user.key().id() == int(post_user_id):
            content = self.request.get('content')

            postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
            key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
            comment = db.get(key)

            comment.content = content
            comment.put()

            self.redirect('/' + post_id)

        else:
            self.write("You don't have permission to edit this comment.")

class DeleteCommentHandler(BlogHandler):

    def get(self, post_id, post_user_id, comment_id):

        if self.user and self.user.key().id() == int(post_user_id):
            postKey = db.Key.from_path('Post', int(post_id), parent=blog_key())
            key = db.Key.from_path('Comment', int(comment_id), parent=postKey)
            comment = db.get(key)
            comment.delete()

            self.redirect('/' + post_id)

        elif not self.user:
            self.redirect('/login')

        else:
            self.write("You don't have permission to delete this comment.")


# Routing

app = webapp2.WSGIApplication([
    ('/', BlogFrontHandler),
    ('/signup', SignupHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),
    ('/newpost', NewPostHandler),
    ('/([0-9]+)', PostHandler),
    ('/([0-9]+)/like', LikePostHandler),
    ('/([0-9]+)/unlike', UnlikePostHandler),
    ('/([0-9]+)/edit', EditPostHandler),
    ('/([0-9]+)/delete/([0-9]+)', DeletePostHandler),
    ('/([0-9]+)/addcomment/([0-9]+)', AddCommentHandler),
    ('/([0-9]+)/([0-9]+)/editcomment/([0-9]+)', EditCommentHandler),
    ('/([0-9]+)/([0-9]+)/deletecomment/([0-9]+)', DeleteCommentHandler)
], debug=True)
