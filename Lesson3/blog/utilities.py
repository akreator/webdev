import re
import hmac
import string
import random
import hashlib

def checkName(name):
    name_re = re.compile(r"^[A-Za-z0-9_-]{3,20}$") #ask for first and last name
    if name_re.match(name):
        return name


def checkPassword(password):
    pass_re = re.compile(r"^.{3,20}$")
    if pass_re.match(password):
        return password


def checkEmail(email):
    if email and len(email) > 0:
        mail_re = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
        if mail_re.match(email):
            return email
        else:
            return False
    return True


def checkValidSignup(name, password, verify, email):
    errors = "~"
    if not checkName(name):
        errors += "Please enter a valid username."
    errors += "~"
    if not checkPassword(password):
        errors += "Please enter a valid password."
    errors += "~"
    if not password == verify:
        errors += "Please make sure the passwords match."
    errors += "~"
    if not checkEmail(email):
        errors += "Please enter a valid email."
    return errors

secret = "JOg*8)!XtTb&c=)R;q}}~Er6zXw5dlSlu7\c=,f^5j#5QCt"

def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


#Copied from Steve because I wrote these for a quiz and forgot to copy them over
def make_salt(length = 5):
    return ''.join(random.choice(string.letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)