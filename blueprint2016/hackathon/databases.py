from google.appengine.ext import db
import re


class Users(db.Model):
    username = db.StringProperty(required=True)
    pronouns = db.StringProperty(required=True)
    progress = db.IntegerProperty(required=True)
    inventory = db.ListProperty(str)


    @classmethod
    def check_valid_values(cls, username, pronouns):
        name_re = re.compile(r"\w{2,16}$")
        pronouns_re = re.compile(r"\w{2,5}/\w{2,5}")
        if name_re.match(username) and pronouns_re.match(pronouns):
            return True
        else:
            return False


    @classmethod
    def register_user(cls, username, pronouns):
        if cls.check_valid_values(username, pronouns):
            user = Users(username=username, pronouns=pronouns, progress=0, inventory=["cell phone", "water bottle"])
            user.put()
            return user
        else:
            return None


class Event(db.Model):
    content = db.TextProperty(required=True)
    location = db.StringProperty(required=True)
    id_num = db.IntegerProperty(required=True)
    user = db.ReferenceProperty(Users)
    parent_event = db.SelfReferenceProperty()
    bgcolor = db.StringProperty()

    def get_child_events(self):
        return self.event_set.get()

    @classmethod
    def get_by_num(self, num):
        e = db.GqlQuery("SELECT * FROM Event WHERE id_num = %s" %(str(num)))
        return e.get()

    @classmethod
    def create_event(cls, content, location, user, parent_event, bgcolor=""):
        length = len(list(cls.all()))
        e = Event(content=content, location=location, id_num=length, user=user, parent_event=parent_event,
                  bgcolor=bgcolor)
        return e


class Trigger(db.Model):
    linked_event = db.ReferenceProperty(Event, collection_name="triggers_to")
    parent_event = db.ReferenceProperty(Event, collection_name="triggers_from")
    item_needed = db.StringProperty()
    item_found = db.StringProperty()
    action = db.StringProperty()


class Comment(db.Model):
    content = db.StringProperty(required=True)
    author = db.ReferenceProperty(Users, required=True)
    likes = db.IntegerProperty(required=True)
    related_event = db.ReferenceProperty(Event)
