import jinja2, webapp2, re, os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape = True)


class Users(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    birthday = db.DateProperty()
    email = db.StringProperty()

    def get_posts(self):
        return self.blog_set.get()

    @classmethod
    def get_posts_by_username(cls, name):
        b = db.GqlQuery("SELECT * FROM Blog WHERE username = %s" % name)
        return b.get_posts()

    @classmethod
    def check_valid_values(cls, username, password, birthday="00/00/0000", email="no@email.given"):
        user_re = re.compile(r"[\w-]{3,}$").match(username)
        password_re = re.compile(r".{4,}$").match(password)
        email_re = re.compile(r".{5,}").match(birthday)
        birthday_re = re.compile(r"\d{1,2}/\d{1,2}/\d{2,4}").match(email)
        if user_re and password_re and email_re and birthday_re:
            return True
        else:
            return False

    @classmethod
    def register(cls, username, password, birthday="", email=""):
        if check_valid_values(username, password, birthday, email):
            user = cls(username=username,
                        password=make_pw_hash(password),
                        birthday=birthday,
                        email=email)
            return user
        else:
            return False


class Blog(db.Model):
    title = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    author = db.StringProperty(Users, required=True)
    datetime = db.DateTimeProperty(auto_now_add=True)
    likes = db.IntegerProperty(required=True)

    def get_comments(self):
        return self.comment_set.get()

    @classmethod
    def make_post(title, content, author):
        b = Blog(title=title, content=content, author=author, likes=0)
        b.put()


class Comment(db.Model):
    content = db.StringProperty(required=True)
    author = db.ReferenceProperty(Users, required=True)
    likes = db.IntegerProperty(required=True)
    related_post = db.ReferenceProperty(Blog)


class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render(self, template, **params):
        t = jinja_env.get_template(template)
        self.write(t.render(params))

    def set_cookie(self, name, value):
        pass

    def make_pw_hash(self, password):
        pass

    def login(cls, username, password):
        user = db.GqlQuery("SELECT * FROM Users WHERE username = %s" % username)
        if user and user.password == password:
            self.set_cookie("user_id", user.key().id())

    def initialize(self, *args, **kwargs):
        webapp2.RequestHandler.initialize(self, *args, **kwargs)
        #self.user


class MainHandler(Handler):
    def get(self):
        blog = db.GqlQuery("SELECT * FROM Blog")
        self.render("front.html")

class LoginHandler(Handler):
    def get(self):
        self.render("login.html")

class SignUpHandler(Handler):
    def get(self):
        self.render("signup.html")

class NewPostHandler(Handler):
    def get(self):
        self.render("newpost.html")

class PostHandler(Handler):
    def get(self):
        self.render("posts.html")

class ProfileHandler(Handler):
    def get(self):
        self.write("profile")

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/login', LoginHandler),
                               ('/signup', SignUpHandler),
                               ('/newpost', NewPostHandler),
                               ('/post', PostHandler),
                               ('/about', ProfileHandler)], debug=True)
