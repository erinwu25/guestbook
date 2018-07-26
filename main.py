import webapp2
import jinja2
import os

import logging

from google.appengine.api import users
from google.appengine.ext import ndb

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True
)

class Message(ndb.Model):
    content = ndb.StringProperty()
    email = ndb.StringProperty()
    created_time = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def get(self):
        login_url = ''
        logout_url = ''
        #current user will be a user object or NONE
        current_user = users.get_current_user()
        #if no one is logged in, show a login prompt
        if not current_user:
            login_url = users.create_login_url('/')
        else:
            logout_url = users.create_logout_url('/')

        #2. read/write from the database
        message_query = Message.query()
        message_query = message_query.order(-Message.created_time)
        messages = message_query.fetch()



        templateVars = {
            'current_user' : current_user,
            'login_url' : login_url,
            'logout_url' : logout_url,
            'messages' : messages,
        }

        template = env.get_template('/templates/guestbook.html')
        self.response.write(template.render(templateVars))

    def post(self):
        #1. get info from Request
        content = self.request.get('content') #<- content is the name from the form
        email = users.get_current_user().email()

        #2. read/write info to the database
        message = Message(content=content, email=email)
        message.put()

        #3. render a response [redirecting to the main page so the user can see their contribution]
        self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainPage)

], debug=True)
