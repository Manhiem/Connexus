import random

import webapp2
from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.api import app_identity

from config import utils
import urllib

import json
import logging

from services import ops


import re
from google.appengine.api import images
import services.lib.cloudstorage as gcs


class ViewSingleStreamHandler(webapp2.RequestHandler):
    def get(self):
        if not users.get_current_user():
            self.redirect(users.create_login_url(self.request.uri))
        else:
            #stream_id = self.request.get('stream_id')
            self.render()

    def getstreamid(self):
        return self.request.get('stream_id')

    def getpagerange(self):
        if not self.request.get('page_range'):
            cur_page_range=4
        else:
            cur_page_range=self.request.get('page_range')
        return cur_page_range

    def render(self):
        #appName = app_identity.get_application_id()
        #self.response.write(stream_id)
        current_user = users.get_current_user().email()
        logout_url = users.create_logout_url(utils.raw_logout_url)
        data = {}
        stream_id= self.request.get('stream_id')


        try:
            rpc = urlfetch.create_rpc()
            request = {}
            request['user_id'] = current_user
            request['stream_id'] = stream_id
            request['page_range'] = self.getpagerange()
            url= 'https://services-dot-pigeonhole-apt.appspot.com/service-viewsinglestream?' + urllib.urlencode(request)

            urlfetch.make_fetch_call(rpc, url)
            response = rpc.get_result()
            data = json.loads(response.content)

        except Exception:
            self.response.write("Error!<br>")
            self.response.write(Exception)


        is_owned=data['is_owned']
        is_subed=data['is_subed']

        pict_list=data['pict_list']
        page_range=data['page_range']

        logout_url = users.create_logout_url(utils.raw_logout_url)
        upload_image_handler_url='/upload_image_handler_url'
        upload_image_servic_url='https://services-dot-pigeonhole-apt.appspot.com/service-uploadimage'
        length=len(pict_list)

        view_single_show_more_handler_url='/view_single_show_more_handler_url'
        view_single_subscribe_handler_url='/view_single_subscribe_handler_url'
        geo_view_handler_url= '/geo_view_handler_url?stream_id='+stream_id

        is_all=False
        if(page_range==len(pict_list)):
            is_all=True

        template_values = {
            'logout_url': logout_url,
            'current_user': current_user,
            'pict_list':pict_list,
            'page_range':page_range,
            'upload_image_handler_url':upload_image_servic_url,
            'stream_id':stream_id,
            'view_single_show_more_handler_url':view_single_show_more_handler_url,
            'is_owned':is_owned,
            'is_subed':is_subed,
            'view_single_subscribe_handler_url':view_single_subscribe_handler_url,
            'is_all':is_all,
            'geo_view_handler_url':geo_view_handler_url
        }


        template = utils.JINJA_ENVIRONMENT.get_template('fresh_view_single_stream.html')
        self.response.write(template.render(template_values))

class ViewSingleShowMoreHandler(webapp2.RequestHandler):
    def get(self):
        page_range= int(self.request.get('page_range'))+4
        page_range= str(page_range)
        stream_id=self.request.get('stream_id')

        self.redirect("/view_single?stream_id="+stream_id+"&page_range="+ page_range)


class ViewSingleSubscribeHandler(webapp2.RequestHandler):
    def get(self):
        current_user = users.get_current_user().email()
        stream_id= self.request.get('stream_id')
        is_subed=self.request.get('is_subed')

        if is_subed == "False":

            try:
                rpc = urlfetch.create_rpc()
                request = {}
                request['user_id'] = current_user
                request['stream_id'] = stream_id
                url= 'https://services-dot-pigeonhole-apt.appspot.com/service-subscribestream?' + urllib.urlencode(request)
                urlfetch.make_fetch_call(rpc, url)

            except Exception:
                self.response.write("Error!<br>")
                self.response.write(Exception)

        else:
            form_fields={
                'unsubscribe_list': stream_id,
                'user_id': current_user
            }
            try:
                form_data = urllib.urlencode(form_fields)
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                result = urlfetch.fetch(
                    url='https://services-dot-pigeonhole-apt.appspot.com/service-unsubscribestream',
                    payload=form_data,
                    method=urlfetch.POST,
                    headers=headers)
                #self.redirect('/manage')

            except urlfetch.Error:
                logging.exception('Caught exception fetching url')

        self.redirect('/view_single?stream_id='+stream_id)


class UploadImageHandler(webapp2.RequestHandler):
    def post(self):

        unicorn = self.request.get('file')
        img_name = self.request.POST['file'].filename
        # img_name = "ohshitfuck"  # self.request.get('img_name')
        stream_id = self.request.get('stream_id')  # self.request.get('stream_id')

        unicorn = images.resize(unicorn, 500, 500)
        # find the right bucket-stream path
        b = "/pigeonhole-apt.appspot.com/" + str(stream_id)

        # much be post!
        img_real_name = self.request.POST['file'].filename
        pat = "(.+)\.(.+)"
        img_real_type = re.match(pat, str(img_real_name)).group(2)

        # construct a new content_type
        content_type_value = "image/" + str(img_real_type).lower()

        # create such file and write to it
        gcs_file = gcs.open(b + "/" + str(img_name), 'w', content_type=content_type_value)
        gcs_file.write(unicorn)
        gcs_file.close()

        unicorn_url = "https://storage.googleapis.com/pigeonhole-apt.appspot.com/" \
                      + str(stream_id) + "/" + str(img_name)

        """
        unicorn_url = self.request.get('img_url')
        img_name = self.request.get('img_name')
        stream_id = self.request.get('stream_id')
        """

        # img_comment = "comment"
        # ops.create_image(img_comment, img_name, unicorn_url, stream_id)
        # # self.redirect(str("https://pigeonhole-apt.appspot.com/view_single?stream_id=" + str(stream_id)))
        lat = - 57.32652122521709 + 114.65304245043419 * random.random()
        lon = - 123.046875 + 246.09375 * random.random()

        form_fields = {
            'img_url': unicorn_url,
            'img_name': str(re.match(pat, str(img_real_name)).group(1)),
            'stream_id': stream_id,
            'lon': lon,
            'lat': lat
        }

        form_data = urllib.urlencode(form_fields)
        headers = {}  # {'Content-Type': 'multipart/form-data'}
        # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        result = urlfetch.fetch(
            url='https://services-dot-pigeonhole-apt.appspot.com/service-secretupload',  # need changing
            payload=form_data,
            method=urlfetch.POST)

