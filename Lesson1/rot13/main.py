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

html = """
<!DOCTYPE html>
<html>
    <head>
        <h1> ROT13 <h1>
        <h3> Enter text here: <h3>
    </head>

    <body>
        <form method="POST">
            <textarea name="text" style="width:300px; height:200px">%(codedText)s</textarea>
            <br>
            <input type="submit">
        </form>
    </body>
</html>
"""

def encodeText(str):
        str = list(str)
        str = [encodeLetter(char) for char in str];
        return ''.join(str)   
def encodeLetter(char):
    if char.isalpha():
        val = ord(char) + 13
        if val > 122 or 90 < val <= 103:
           val -= 26       
        return chr(val)
    return char 
def escape_html(s):
    return cgi.escape(s, quote = True)    

class MainHandler(webapp2.RequestHandler):
    def createPage(self, codedText=""):
        self.response.out.write(html %{"codedText" : codedText})
        
    def get(self):
        self.createPage()      
    def post(self):
        text = encodeText(self.request.get("text"))
        self.createPage(escape_html(text))               


app = webapp2.WSGIApplication([('/', MainHandler)], debug=True)
