import jinja2
import os
import webapp2

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
autoescape = True)


hidden_html = """
<input type="hidden" name="food" value="%s">
"""

shopping_list_html = """
<br>
<br>
<h2>Shopping List</h2>
<ul>
%s
</ul>
"""

item_html = "<li>%s</li>"

class Handler(webapp2.RequestHandler):    
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
        
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))
        
class MainHandler(Handler):
    def get(self):
        items = self.request.get_all('food')
        self.render("shopping_list.html", items = items)
        

class FizzBuzzHandler(Handler):
    def get(self):
        n = self.request.get("n")
        if n:
            n = int(n)
        else:
            n = 0
        self.render("fizzbuzz.html", n=n, gotit="MADE IT TO THE END, Y'ALL")
  

app = webapp2.WSGIApplication([('/', MainHandler),
                               ('/fizzbuzz', FizzBuzzHandler)], debug=True)
