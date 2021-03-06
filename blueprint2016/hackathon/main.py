import jinja2, webapp2, re, os
import databases as my_db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=True)


class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render(self, template, **params):
        t = jinja_env.get_template(template)
        self.write(t.render(params))

    def reset(self):
        self.set_cookie("userid", "")

    def set_cookie(self, name, value):
        self.response.headers.add_header('set-cookie', '%s=%s; path=/' % (name, value))

    def initialize(self, *args, **kwargs):
        webapp2.RequestHandler.initialize(self, *args, **kwargs)
        uid = self.request.cookies.get("userid")
        if uid and uid.isdigit():
            self.user = my_db.Users.get_by_id(int(uid))
            if not self.user:
                self.set_cookie('userid', '')
        else:
            self.user = None


class MainHandler(Handler):
    def get(self):
        if self.user:
            self.redirect('/welcome')
        else:
            self.render("start.html", error="")

    def post(self):
        username = self.request.get("username")
        pronouns = self.request.get("pronouns")
        if username and pronouns:
            u = my_db.Users.register_user(username, pronouns)
            if u:
                self.set_cookie("userid", str(u.key().id()))
                self.redirect('/0')
        self.render("start.html", error="Please enter valid values")


class EventHandler(Handler):
    def render_event(self, event, current_page, error=""):
        self.render("event.html", event=event, save_page=current_page, user=self.user, error="")

    def get(self, idnum):
        e = my_db.Event.get_by_num(int(idnum))
        if self.user and e:
            if self.request.get("new") != "true":
                self.user.path.append(e.location)
                self.user.put()
            self.render_event(event=e, error="", current_page=idnum)
        else:
            self.redirect('/')

    def post(self, idnum):
        next_event = self.request.get("next_event")
        if next_event == "custom":
            self.redirect('/%s/newpath' % idnum)
        elif next_event:
            e = my_db.Event.get_by_id(int(next_event))
            if (not e.item_needed) or (e.item_needed in self.user.inventory):
                if e.item_needed:
                    self.user.inventory.remove(e.item_needed)
                if e.item_found:
                    self.user.inventory.append(e.item_found)
                self.user.put()
                self.redirect("/%s" % str(e.id_num))
            else:
                self.render_event(event=my_db.Event.get_by_num(int(idnum)), current_page=idnum,
                                  error="You do not have the item needed for this action!")
        else:
            self.render_event(event=my_db.Event.get_by_num(int(idnum)), current_page=idnum,
                              error="Please choose an action.")


class NewEventHandler(Handler):
    def get(self, parent_num):
        self.render("newpath.html", error="", save_page=parent_num)

    def post(self, parent_num):
        content = self.request.get("content")
        location = self.request.get("location")
        bgcolor = self.request.get("bgcolor")
        text_color = self.request.get("text_color")
        item_needed = self.request.get("item_needed").lower()
        item_found = self.request.get("item_found").lower()
        action = self.request.get("action")
        parent_event = my_db.Event.get_by_num(int(parent_num))

        if content and location and action:
            e = my_db.Event.create_event(content=content, location=location, action=action,
                                         parent_event=parent_event, user=self.user, bgcolor=bgcolor,
                                         text_color=text_color, item_needed=item_needed, item_found=item_found)
            e.put()
            self.redirect('/%s?new=true' % parent_num)
        else:
            self.render("newpath.html", error="Please make sure you have a location and content", save_page=parent_num)


class SetUpHandler(Handler):
    def get(self):
        pass


class RestartHandler(Handler):
    def get(self):
        self.reset()
        self.redirect('/')


class FeedbackHandler(Handler):
    def get(self):
        self.render("feedback.html")


class ContactHandler(Handler):
    def get(self):
        self.render("contact.html")


class SaveHandler(Handler):
    def get(self):
        save_point = self.request.get("save_point")
        if save_point:
            self.user.save_point = int(save_point)
            self.user.put()
        self.redirect('/%s?new=true' % save_point)


class AboutHandler(Handler):
    def get(self):
        self.render("about.html")


class WelcomeHandler(Handler):
    def get(self):
        if self.user:
            self.render("welcome.html", user=self.user)
        else:
            self.redirect('/')

    def post(self):
        if self.user.save_point and self.user.save_point > 0:
            self.redirect("%s?new=true" % self.user.save_point)
        else:
            self.redirect('/0?new=true')


app = webapp2.WSGIApplication([('/', MainHandler),
                               (r'/(\d+)', EventHandler),
                               (r'/(\d+)/newpath', NewEventHandler),
                               ('/restart', RestartHandler),
                               ('/feedback', FeedbackHandler),
                               ('/contact', ContactHandler),
                               (r'/save', SaveHandler),
                               ('/about', AboutHandler),
                               ('/welcome', WelcomeHandler)], debug=True)
