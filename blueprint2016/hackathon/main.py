import jinja2, webapp2, re, os
import databases as my_db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self, *args, **kwargs):
        self.response.out.write(*args, **kwargs)

    def render(self, template, **params):
        t = jinja_env.get_template(template)
        self.write(t.render(params))

    def reset(self):
        self.set_cookie("userid", "")

    def set_cookie(self, name, value):
        self.response.headers.add_header('set-cookie', '%s=%s; path=/' %(name, value))

    def initialize(self, *args, **kwargs):
        webapp2.RequestHandler.initialize(self, *args, **kwargs)
        uid = self.request.cookies.get("userid")
        if uid and uid.isdigit():
            self.user = my_db.Users.get_by_id(int(uid))
        else:
            self.user = None


class MainHandler(Handler):
    def get(self):
        if self.user and self.user.progress and self.user.progress > 0:
            self.redirect('%s' %str(self.user.progress))
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
    def get(self, idnum):
        self.render("event.html", event=my_db.Event.get_by_num(int(idnum)), user=self.user, latest=idnum, error="")

    def post(self, idnum):
        trigger_id = self.request.get("trigger")
        if trigger_id == "custom":
            self.redirect('/%s/newpath' %idnum)
        elif trigger_id:
            t = my_db.Trigger.get_by_id(int(trigger_id))
            if (not t.item_needed) or (t.item_needed in self.user.inventory):
                if t.item_needed:
                    self.user.inventory.remove(t.item_needed)
                if t.item_found:
                    self.user.inventory.append(t.item_found)
                self.user.put()
                self.redirect("/%s" %str(t.linked_event.id_num))
            else:
                self.render("event.html", event=my_db.Event.get_by_num(int(idnum)), user=self.user, error="You do not have the item needed for this action!")
        else:
            self.render("event.html", event=my_db.Event.get_by_num(int(idnum)), user=self.user, latest=idnum, error="Please choose an action.")

class NewEventHandler(Handler):
    def get(self, parent_num):
        self.render("newpath.html", error="")

    def post(self, parent_num):
        content = self.request.get("content")
        location = self.request.get("location")
        background = self.request.get("bgcolor")
        item_needed = self.request.get("item_needed").lower()
        item_found = self.request.get("item_found").lower()
        action = self.request.get("action")
        user = self.user
        parent_event = my_db.Event.get_by_num(int(parent_num))

        if content and location and action:
            e = my_db.Event.create_event(content=content, location=location,
                                         user=user, parent_event=parent_event,
                                         bgcolor=background)
            e.put()
            t = my_db.Trigger(linked_event=e, parent_event=parent_event, item_needed=item_needed, item_found=item_found,
                              action=action)
            t.put()
            self.redirect('/%s' %parent_num)
        else:
            self.render("newpath.html", error="Please make sure you have a location and content")


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
        progress = self.request.get("progress")
        if progress:
            self.user.progress = int(progress)
            self.user.put()
        self.redirect('/%s' %progress)

class AboutHandler(Handler):
    def get(self):
        self.render("about.html")


app = webapp2.WSGIApplication([('/', MainHandler),
                               (r'/(\d+)', EventHandler),
                               (r'/(\d+)/newpath', NewEventHandler),
                               ('/restart', RestartHandler),
                               ('/feedback', FeedbackHandler),
                               ('/contact', ContactHandler),
                               (r'/save', SaveHandler),
                               ('/about', AboutHandler)], debug=True)
