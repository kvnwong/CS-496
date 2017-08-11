from google.appengine.ext.webapp import template
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from random import randint
import webapp2
import urllib
import random
import string
import json
import os

CLIENT_ID = '168052706527-dkri7eta1m4v79sq668rc974jnk1pgtm.apps.googleusercontent.com'
CLIENT_SECRET = 'sL_Uy_wbmbLCCNAQiFx_z-wL'
REDIRECT_URI = 'http://localhost:8080/oauth'
CURRENT_USER_ID = " "


class CryptoPortfolio(ndb.Model):
    id = ndb.StringProperty()
    asset1 = ndb.StringProperty()
    asset2 = ndb.StringProperty()
    asset3 = ndb.StringProperty()
    asset4 = ndb.StringProperty()

class CryptoGlobal(ndb.Model):
    id = ndb.StringProperty()
    total_market_cap_usd = ndb.IntegerProperty()
    total_24h_volume_usd = ndb.IntegerProperty()
    bitcoin_percentage_of_market_cap = ndb.IntegerProperty()
    active_currencies = ndb.StringProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        random_string = ''.join([random.choice(string.ascii_letters + string.digits) for n in xrange(32)])

        url = "https://accounts.google.com/o/oauth2/v2/auth?"
        url = url + "scope=email"
        url = url + "&access_type=offline"
        url = url + "&include_granted_scopes=true"
        url = url + "&state="
        url = url + random_string
        url = url + "&redirect_uri=http://localhost:8080/oauth"
        url = url + "&response_type=code"
        url = url + "&client_id=168052706527-dkri7eta1m4v79sq668rc974jnk1pgtm.apps.googleusercontent.com"

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
            url = "https://www.googleapis.com/oauth2/v4/token",
   		 	payload = payload,
    		method = urlfetch.POST,
    		headers = headers)

        json_result = json.loads(result.content)

        headers = {'Authorization': 'Bearer ' + json_result['access_token']}
        result = urlfetch.fetch(
            url = "https://www.googleapis.com/plus/v1/people/me",
            method = urlfetch.GET,
            headers = headers)

        json_result = json.loads(result.content)
        fname = json_result['name']['givenName']
        lname = json_result['name']['familyName']
        CURRENT_USER_ID = json_result['id']

        template_values = {'fname': fname,
                           'lname': lname,
                           'user_id': CURRENT_USER_ID}

        result = urlfetch.fetch("https://api.coinmarketcap.com/v1/ticker")

        json_crypto_assests = json.loads(result.content)

        result = urlfetch.fetch("https://api.coinmarketcap.com/v1/global")

        json_global_crypto = json.loads(result.content)

        random_number = randint(0,int(json_global_crypto['active_currencies']))

        template_values['user_id'] = random_number



        path = os.path.join(os.path.dirname(__file__), 'templates/oauth.html')
        self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth',OAuthHandler)
], debug=True)
