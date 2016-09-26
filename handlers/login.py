from handlers.blog import BlogHandler
from models.user import User

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