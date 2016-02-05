import jinja2
import os
import webapp2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blog(db.Model): #class name = name of table (class IS table)
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    time_posted = db.DateTimeProperty(auto_now_add = True)
    date_posted = db.DateProperty(auto_now_add = True)


class FrontHandler(Handler):
    def get(self):
        #blog = Blog.all();
        blog = db.GqlQuery("SELECT * FROM Blog ORDER BY time_posted DESC LIMIT 10")
        self.render("front.html", blog=blog)


class NewHandler(Handler):
    def render_page(self, title="", content="", error=""):
        self.render("newpost.html", title=title, content=content, error=error)

    def get(self):
        self.render_page()

    def post(self):
        title = self.request.get("title")
        content = self.request.get("content")

        if title and len(content) > 0:
            b = Blog(title = title, content = content)
            b.put()
            id_num = str(b.key().id())
            self.redirect("/%s" % id_num)
        else:
            error = "Please enter both a title and some content"
            self.render_page(title, content, error)


class PostHandler(Handler):
    def render_post(self, post="", error=""):
        self.render("post.html", post=post, error=error)

    def get(self, id_num):
        id_num = int(id_num)
        post = Blog.get_by_id(id_num)
        if post:
            error=""
        else:
            error="Sorry, that post doesn't exist."
        self.render_post(post=post, error=error)

    def post(self, id_num):
        self.redirect("/")

app = webapp2.WSGIApplication([('/', FrontHandler), ('/newpost', NewHandler), (r'/(\d+)', PostHandler)], debug=True)
