import jinja2, webapp2, os, re

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render(self, template, **params):
        t = jinja_env.get_template(template)
        self.write(t.render(params))

    def set_cookie(self, name, value):
        self.response.headers.add_header('set-cookie', '%s=%s; path=/' % (name, value))



class MainHandler(Handler):
    def get(self):
        self.render('index.html');
    def post(self):
        username = self.request.get('username')
        email = self.request.get('email')
        password = self.request.get('password')
        self.render('index.html', username=username, password=password, email=email)


app = webapp2.WSGIApplication([('/', MainHandler)], debug=True)
