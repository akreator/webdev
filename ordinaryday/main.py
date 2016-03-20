import jinja2, webapp2, re, os, datetime
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
        expiration_date = datetime.datetime.now() + datetime.timedelta(weeks=52)
        self.response.set_cookie(name, value, expires=expiration_date, path='/')

    def initialize(self, *args, **kwargs):
        webapp2.RequestHandler.initialize(self, *args, **kwargs)
        uid = self.request.cookies.get("userid")
        if uid and uid.isdigit():
            self.user = my_db.Users.get_by_id(int(uid))
            if not self.user:
                self.set_cookie('userid', '')
        else:
            self.user = None

    def parse_content(self, content):
        content = content.replace('<name>', self.user.username)
        content = content.replace('<they>', self.user.pronouns.split('/')[0])\
                         .replace('<them>', self.user.pronouns.split('/')[1])\
                         .replace('<their>', self.user.pronouns.split('/')[2])\
                         .replace('<theirs>', self.user.pronouns.split('/')[3])
        return content


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
        self.render("start.html", error="Please enter a valid name: letters only.")


class EventHandler(Handler):
    def render_event(self, event, current_page, error=""):
        self.render("event.html", event=event, user=self.user, error=error, parse_content=self.parse_content)

    def get(self, idnum):
        e = my_db.Event.get_by_num(int(idnum))
        if self.user and e:
            if self.request.get("new") != "true":
                if not self.user.path or self.user.path[-1] != e.location:
                    self.user.path.append(e.location)
                self.user.progress.append(e.id_num)
                self.user.put()
            self.render_event(event=e, error="", current_page=idnum)
        else:
            if self.user:
                self.redirect('/%s?new=true' % self.user.progress[-1])
            else:
                self.redirect('/')

    def post(self, idnum):
        next_event = self.request.get("next_event")
        if next_event == "custom":
            self.redirect('/%s/newpath' % idnum)
        elif next_event == "edit":
            self.redirect('/%s/newpath?edit=true' % idnum)
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
        if self.request.get("edit"):
            e = my_db.Event.get_by_num(int(parent_num))
            self.render("newpath.html", error="", content=e.content, location=e.location, bgcolor=e.bgcolor,
                        text_color=e.text_color, item_needed=e.item_needed, item_found=e.item_found, action=e.action,
                        editting=True)
        else:
            self.render("newpath.html", error="")

    def post(self, parent_num):
        content = self.request.get("content")
        location = self.request.get("location")
        bgcolor = self.request.get("bgcolor")
        text_color = self.request.get("text_color")
        item_needed = self.request.get("item_needed").lower()
        item_found = self.request.get("item_found").lower()
        action = self.request.get("action")
        parent_event = my_db.Event.get_by_num(int(parent_num))

        if content and location and action and action.lower() != 'walk your own path':
            if self.request.get('edit'):
                my_db.Event.update_event(id_num=parent_num, content=content, location=location, action=action,
                                         bgcolor=bgcolor, item_needed=item_needed, item_found=item_found)
            else:
                e = my_db.Event.create_event(content=content, location=location, action=action,
                                             parent_event=parent_event, user=self.user, bgcolor=bgcolor,
                                             text_color=text_color, item_needed=item_needed, item_found=item_found)
                e.put()
            self.redirect('/%s?new=true' % parent_num)
        else:
            self.render('newpath.html', error='Please make sure you have a location, action, and content',
                        content=content, location=location, bgcolor=bgcolor, text_color=text_color,
                        item_needed=item_needed, item_found=item_found, action=action)


class RestartHandler(Handler):
    def get(self):
        self.reset()
        self.redirect('/')


class FeedbackHandler(Handler):
    def get(self):
        self.render("feedback.html")

    def post(self):
        name = self.request.get("name")
        email = self.request.get("email")
        feedback = self.request.get("feedback")

        if name and email and feedback:
            message = """
                From: anordinarydaygame@gmail.com
                To: Audrey Kintisch akintisch@gmail.com
                Subject: Ordinary Day Feedback

                User: %s %s
                %s
                """ % (name, email, feedback)
            f = my_db.Feedback.log_feedback(name=name, email=email, feedback=message)
            if f:
                self.render('feedback.html', error='Your response has been recorded.')
            else:
                self.render('feedback.html', error='Please enter a valid e-mail address.')
        else:
            self.render('feedback.html', error='Please enter values for all fields.')


class ContactHandler(Handler):
    def get(self):
        self.render("contact.html")


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
        if len(self.user.progress) > 0:
            self.redirect("%s?new=true" % self.user.progress[-1])
        else:
            self.redirect('/0')


app = webapp2.WSGIApplication([('/', MainHandler),
                               (r'/(\d+)', EventHandler),
                               (r'/(\d+)/newpath', NewEventHandler),
                               ('/restart', RestartHandler),
                               ('/feedback', FeedbackHandler),
                               ('/contact', ContactHandler),
                               ('/about', AboutHandler),
                               ('/welcome', WelcomeHandler)], debug=True)
