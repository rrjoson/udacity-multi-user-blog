from handlers.blog import BlogHandler
from models.user import User
from helpers import *

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