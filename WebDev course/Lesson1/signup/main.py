#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import re

html = """
<!DOCTYPE html>
<html>
    <head>
        <h1>Sign Up:</h1>
    </head>

    <body>
        <form method="POST">
            <label> Username:
                <input type="text" name="username" value="%(username)s">
            </label> %(nameerror)s
            <br>
            <br>
            <label> Password:
                <input type="password" name="password">
            </label> %(passworderror)s
            <br>
            <br>
            <label> Verify Password:
                <input type="password" name="verify">
            </label> %(verifyerror)s
            <br>
            <br>
            <label> E-mail: (Optional)
                <input type="text" name="email" value=%(email)s>
            </label> %(emailerror)s
            <br>
            <br>
            <input type="submit">
        </form>
    </body>
</html>
""" 

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

def checkValid(name, password, verify, email):
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

class MainHandler(webapp2.RequestHandler):    
    def createPage(self, username="", email="", nameerror="", passworderror="", verifyerror="", emailerror = ""):
        self.response.out.write(html %{"username" : cgi.escape(username, quote=True), "email" : cgi.escape(email, quote=True), 
                                      "nameerror" : nameerror, "passworderror" : passworderror,
                                      "verifyerror" : verifyerror, "emailerror" : emailerror})

    def get(self):
        self.createPage()      
    def post(self):
        errors = re.findall(r"~[^~]*", checkValid(self.request.get("username"),
                                               self.request.get("password"),
                                               self.request.get("verify"),
                                               self.request.get("email")))
        if all(e is '~' for e in errors):
            self.redirect("/welcome?name=%s" %self.request.get("username"))
        else:
            self.createPage(self.request.get("username"), self.request.get("email"), 
                            errors[0][1:], errors[1][1:], errors[2][1:], errors[3][1:])    
        
class WelcomeHandler(webapp2.RequestHandler):
    def get(self):
        name = self.request.get("name")
        if re.match(r"adora.*", name.lower()):
            name = "GIANT BAG OF DICKS"
        self.response.out.write("Wecome, %s!" %name) 


app = webapp2.WSGIApplication([('/', MainHandler),
                               ("/welcome", WelcomeHandler)], debug=True)
