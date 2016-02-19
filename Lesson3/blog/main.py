import jinja2
import os
import webapp2
import re
import utilities
import json


from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape = True)


class Blog(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    username = db.StringProperty(required=True)
    time_posted = db.DateTimeProperty(auto_now_add=True)
    date_posted = db.DateProperty(auto_now_add=True)

    def to_dict(self):
        bdict = { "title" : self.title,
                  "content" : self.content,
                  "username": self.username,
                  "time_posted" : str(self.time_posted),
                  "post_id": str(self.key().id()) }
        return bdict


class Users(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = utilities.make_pw_hash(name, pw)
        return Users(username=name, password=pw_hash, email=email)

    @classmethod
    def get_by_username(cls, username):
        user = db.GqlQuery("SELECT * FROM Users WHERE username=:1", username).get()
        return user

    @classmethod
    def check_login(cls, name, pw):
        user = cls.get_by_username(name)
        if user and utilities.valid_pw(name, pw, user.password):
            return user


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = utilities.make_secure_val(val)
        self.response.headers.add_header('set-cookie', '%s=%s; path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and utilities.check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('userid', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('set-cookie', 'userid=; path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('userid')
        self.user = uid and Users.get_by_id(int(uid))

    def create_json(self, blog):
        if len(blog) > 1:
            posts = []
            for b in blog:
                posts.append(b.to_dict())
            return json.dumps(posts)
        elif blog:
            return json.dumps(blog[0].to_dict())



class FrontHandler(Handler):
    def get(self):
        blog = db.GqlQuery("SELECT * FROM Blog ORDER BY time_posted DESC LIMIT 10")
        blog = list(blog)
        self.render("front.html", blog=blog, user=self.user)


class NewHandler(Handler):
    def render_page(self, title="", content="", error=""):
        self.render("newpost.html", title=title, content=content, error=error)

    def get(self):
        if self.user:
            self.render_page()
        else:
            self.redirect('/login')

    def post(self):
        title = self.request.get("subject")
        content = self.request.get("content")

        if title and len(content) > 0:
            b = Blog(title = title, content = content, username = self.user.username)
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


class SignupHandler(Handler):
    def render_page(self, username="", email="", nameerror="", passworderror="", verifyerror="", emailerror="", nametaken=""):
        self.render("signup.html", username=username, email=email, nameerror=nameerror,
                    passworderror=passworderror, verifyerror=verifyerror, emailerror=emailerror,
                    nametaken=nametaken)

    def get(self):
        self.render_page()

    def post(self):
        errors = re.findall(r"~[^~]*", utilities.checkValidSignup(self.request.get("username"), self.request.get("password"),
                                                                  self.request.get("verify"), self.request.get("email")))
        if all(e is '~' for e in errors):
            if not Users.get_by_username(self.request.get("username")):
                newuser = Users.register(self.request.get("username"),
                                         self.request.get("password"),
                                         self.request.get("email"))
                newuser.put()
                self.login(newuser)
                self.redirect('/')
            else:
                self.render_page(username=self.request.get("username"), email=self.request.get("email"),
                                 nametaken="Sorry, but that username has been taken.  Please pick another.")
        else:
            self.render_page(self.request.get("username"), self.request.get("email"),
                            errors[0][1:], errors[1][1:], errors[2][1:], errors[3][1:])


class LoginHandler(Handler):
    def render_page(self, invalidlogin="", username=""):
        self.render("login.html", invalidlogin=invalidlogin, username=username)

    def get(self):
        self.render_page()

    def post(self):
        user = Users.check_login(self.request.get("username"), self.request.get("password"))
        if user:
            self.set_secure_cookie('userid', str(user.key().id()))
            self.redirect('/welcome')
        else:
            self.render_page(invalidlogin="Invalid login", username=self.request.get("username"))


class WelcomeHandler(Handler):
    def get(self):
        if self.user:
            self.response.out.write("Welcome, %s!" % self.user.username)
        else:
            self.redirect('/login')


class LogoutHandler(Handler):
    def get(self):
        self.logout()
        self.redirect('/signup')


class MainJSONHandler(Handler):
    def get(self):
        blog = db.GqlQuery("SELECT * FROM Blog ORDER BY time_posted DESC LIMIT 10")
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(self.create_json(list(blog)))


class PermalinkJSONHandler(Handler):
    def get(self, post_id):
        post = Blog.get_by_id(int(post_id))
        if post:
            self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
            self.write(self.create_json([post]))
        else:
            self.write("Post not found.")


app = webapp2.WSGIApplication([('/', FrontHandler),
                               ('/newpost', NewHandler),
                               (r'/(\d+)', PostHandler),
                               ('/signup', SignupHandler),
                               ('/welcome', WelcomeHandler),
                               ('/login', LoginHandler),
                               ('/logout', LogoutHandler),
                               ('/\.json', MainJSONHandler),
                               (r'/(\d+)\.json', PermalinkJSONHandler)], debug=True)
