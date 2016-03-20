from google.appengine.ext import db
import re


class Users(db.Model):
    username = db.StringProperty(required=True)
    pronouns = db.StringProperty(required=True)
    progress = db.ListProperty(int)
    path = db.ListProperty(str)
    inventory = db.ListProperty(str)
    joined = db.DateTimeProperty(auto_now_add=True)
    last_active = db.DateTimeProperty(auto_now=True)

    def get_events(self):
        return self.event_set()

    @classmethod
    def check_valid_values(cls, username, pronouns):
        name_re = re.compile(r"\w{2,16}$")
        pronouns_re = re.compile(r"[a-zA-Z]{2,5}/[a-zA-Z]{2,5}/[a-zA-Z]{2,5}/[a-zA-Z]{2,5}")
        if name_re.match(username) and pronouns_re.match(pronouns):
            return True
        else:
            return False


    @classmethod
    def register_user(cls, username, pronouns):
        if cls.check_valid_values(username, pronouns):
            user = Users(username=username, pronouns=pronouns, inventory=[])
            user.put()
            return user
        else:
            return None


class Event(db.Model):
    content = db.TextProperty(required=True)
    location = db.StringProperty(required=True)
    action = db.StringProperty(required=True)
    id_num = db.IntegerProperty(required=True)
    parent_event = db.SelfReferenceProperty(collection_name="child_events")
    user = db.ReferenceProperty(Users)
    bgcolor = db.StringProperty()
    text_color = db.StringProperty()
    item_needed = db.StringProperty()
    item_found = db.StringProperty()
    date_created = db.DateTimeProperty(auto_now_add=True)


    @classmethod
    def get_by_num(self, num):
        e = db.GqlQuery("SELECT * FROM Event WHERE id_num = %s" %(str(num)))
        return e.get()

    @classmethod
    def create_event(cls, content, location, action, parent_event, user, bgcolor="", text_color="", item_needed="", item_found=""):
        length = len(list(cls.all()))
        e = Event(content=content, location=location, action=action, parent_event=parent_event, id_num=length, user=user,
                  bgcolor=bgcolor, text_color=text_color, item_needed=item_needed, item_found=item_found)
        return e

    @classmethod
    def update_event(cls, id_num, content, location, action, bgcolor="", text_color="", item_needed="", item_found=""):
        e = Event.get_by_num(id_num)
        e.content = content
        e.location = location
        e.action = action
        e.bgcolor = bgcolor
        e.text_color = text_color
        e.item_needed = item_needed
        e.item_found = item_found
        e.put()


class Feedback(db.Model):
    name = db.StringProperty(required=True)
    email = db.StringProperty(required=True)
    feedback = db.TextProperty(required=True)

    @classmethod
    def log_feedback(cls, name, email, feedback):
        email_re = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
        if email_re.match(email):
            f = Feedback(name=name, email=email, feedback=feedback)
            return f


class Comment(db.Model):
    content = db.StringProperty(required=True)
    author = db.ReferenceProperty(Users, required=True)
    likes = db.IntegerProperty(required=True)
    related_event = db.ReferenceProperty(Event)
