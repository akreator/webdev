from google.appengine.ext import db
import re


class Users(db.Model):
    username = db.StringProperty(required=True)
    pronoun1 = db.StringProperty(required=True)
    pronoun2 = db.StringProperty(required=True)
    save_point = db.IntegerProperty()
    path = db.ListProperty(str)
    inventory = db.ListProperty(str)
    joined = db.DateTimeProperty(auto_now_add=True)
    last_active = db.DateTimeProperty(auto_now=True)

    def get_events(self):
        return self.event_set()

    @classmethod
    def check_valid_values(cls, username, pronouns):
        name_re = re.compile(r"\w{2,16}$")
        pronouns_re = re.compile(r"[a-zA-Z]{2,5}/[a-zA-Z]{2,5}")
        if name_re.match(username) and pronouns_re.match(pronouns):
            return True
        else:
            return False


    @classmethod
    def register_user(cls, username, pronouns):
        if cls.check_valid_values(username, pronouns):
            user = Users(username=username, pronoun1=pronouns.split('/')[0], pronoun2=pronouns.split('/')[1],
                         save_point=0, inventory=["cell phone", "water bottle"])
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


# class Trigger(db.Model):
#    linked_event = db.ReferenceProperty(Event, collection_name="triggers_to")
 #   parent_event = db.ReferenceProperty(Event, collection_name="triggers_from")
  #  item_needed = db.StringProperty()
   # item_found = db.StringProperty()
    #action = db.StringProperty()


class Comment(db.Model):
    content = db.StringProperty(required=True)
    author = db.ReferenceProperty(Users, required=True)
    likes = db.IntegerProperty(required=True)
    related_event = db.ReferenceProperty(Event)
