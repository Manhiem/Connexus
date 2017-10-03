

import webapp2
from google.appengine.api import users
from config import utils
import urllib
from google.appengine.api import urlfetch
import logging

class CreateNewStreamPageHandler(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            self.render()

    def render(self):
        current_user = users.get_current_user().email()
        logout_url = users.create_logout_url(utils.raw_logout_url)
        create_stream_url="/create_stream_url"
        template_values = {
            'logout_url': logout_url,
            'current_user': current_user,
            'create_stream_url':create_stream_url
        }
        template = utils.JINJA_ENVIRONMENT.get_template('fresh_create_stream.html')
        self.response.write(template.render(template_values))

class CreateNewStreamRequestHandler(webapp2.RequestHandler):
    form_fields={}
    def post(self):
        current_user = users.get_current_user().email()

        form_fields={
            'user_id':current_user,
            'name': "hopefullySuccess"
        }

        try:
            form_data = urllib.urlencode(form_fields)
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            result = urlfetch.fetch(
                url='https://services-dot-hallowed-forge-181415.appspot.com/service-test', #need changing
                payload=form_data,
                method=urlfetch.POST,
                headers=headers)
            self.response.write(result.content)
            #self.redirect('/manage')


        except urlfetch.Error:
            logging.exception('Caught exception fetching url')
