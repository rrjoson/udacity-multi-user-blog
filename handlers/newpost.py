from handlers.blog import BlogHandler
from models.post import Post
from helpers import *

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