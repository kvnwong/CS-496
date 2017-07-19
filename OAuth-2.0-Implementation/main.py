from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
import webapp2
import urllib
import random
import string
import json
import os

CLIENT_ID = '913425740949-0c0i284ks9elrosgpv5rdh2qvsal8cim.apps.googleusercontent.com'
CLIENT_SECRET = 'tKkgsZh6HK2zWcNeOrlE9kH3'
REDIRECT_URI = 'https://oauth2-imp.appspot.com/oauth'

class MainPage(webapp2.RequestHandler):
    def get(self):
        random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])

        url_linktext = 'Provide Access'

        url = "https://accounts.google.com/o/oauth2/v2/auth?"
        url = url + "scope=email"
        url = url + "&access_type=offline"
        url = url + "&include_granted_scopes=true"
        url = url + "&state="
        url = url + random_string
        url = url + "&redirect_uri=https://oauth2-imp.appspot.com/oauth"
        url = url + "&response_type=code"
        url = url + "&client_id=913425740949-0c0i284ks9elrosgpv5rdh2qvsal8cim.apps.googleusercontent.com"

        template_values = {'url': url}

        path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(path, template_values))

class OAuthHandler(webapp2.RequestHandler):
    def get(self):
        auth_code = self.request.GET['code']
        state = self.request.GET['state']
        post_body = {
            'code': auth_code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'
            }

        payload = urllib.urlencode(post_body)
        headers = {'Content-Type':'application/x-www-form-urlencoded'}
        result = urlfetch.fetch(
            url="https://www.googleapis.com/oauth2/v4/token",
   		 	payload = payload,
    		method = urlfetch.POST,
    		headers = headers)

        json_result = json.loads(result.content)

        headers = {'Authorization': 'Bearer ' + json_result['access_token']}
        result = urlfetch.fetch(
            url="https://www.googleapis.com/plus/v1/people/me",
            method = urlfetch.GET,
            headers=headers)

        json_result = json.loads(result.content)
        # self.response.write(json.dumps(json_result['name']['givenName']))
        exist_fname = False
        exist_lname = False
        exist_gplink = False
        exist_account = False
        for item in json_result:
            if item == 'name':
                if item[0]:
                    exist_fname = True
                if item[0]:
                    exist_lname = True
            if item == 'url':
                exist_gplink = True

        if exist_fname and exist_lname and exist_gplink:
            fname = json_result['name']['givenName']
            lname = json_result['name']['familyName']
            gplink = str(json_result['url'])
            exist_account = True
            template_values = {'fname': fname,
                               'lname': lname,
                               'gplink': gplink,
                               'gplink_name': "Visit Profile",
                               'state': state}
        else:
            template_values = {'noAccount': "NOTE: No Google+ account found", 'state': state}

        path = os.path.join(os.path.dirname(__file__), 'templates/oauth.html')
        self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth',OAuthHandler)
], debug=True)
