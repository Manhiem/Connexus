
import webapp2
from google.appengine.api import users
from config import utils
from google.appengine.api import urlfetch
import urllib
import json

class ViewAllStreamsHandler(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            self.render()

    def render(self):
        data = {}
        logout_url = users.create_logout_url(utils.raw_logout_url)
        current_user = users.get_current_user().email()

        try:
            rpc = urlfetch.create_rpc()
            request = {}
            request['user_id'] = current_user
            #request['stream_id'] = stream_id
            url= 'https://services-dot-pigeonhole-apt.appspot.com/service-viewallstreams?' + urllib.urlencode(request)

            urlfetch.make_fetch_call(rpc, url)
            response = rpc.get_result()
            data = json.loads(response.content)

        except Exception:
            self.response.write("Error!<br>")
            self.response.write(Exception)

        stream_list=data['all_stream_list']
        list_with_url=[]
        for stream in stream_list:
            stream_with_url=[]
            stream_with_url.append(stream['CoverPage']) #s0
            view_stream_url="/view_single?stream_id="+ stream['Name']
            stream_with_url.append(view_stream_url) #s1
            stream_with_url.append(stream['Name']) #s2
            list_with_url.append(stream_with_url)

        #page_range=data['page_range']
        logout_url = users.create_logout_url(utils.raw_logout_url)

        template_values = {
            'logout_url': logout_url,
            'current_user': current_user,
            'stream_list':stream_list,
            'stream_list_with_url':list_with_url
        }


        template = utils.JINJA_ENVIRONMENT.get_template('fresh_view_all_streams.html')
        self.response.write(template.render(template_values))
