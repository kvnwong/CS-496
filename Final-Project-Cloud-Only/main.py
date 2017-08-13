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


class CryptoAsset(ndb.Model):
    id = ndb.StringProperty()
    user_id = ndb.StringProperty()
    name = ndb.StringProperty()
    symbol = ndb.StringProperty()
    rank = ndb.StringProperty()
    price_usd = ndb.StringProperty()


class UserAccount(ndb.Model):
    id = ndb.StringProperty()
    user_id = ndb.StringProperty()
    fname = ndb.StringProperty()
    lname = ndb.StringProperty()
    email = ndb.StringProperty()


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
        user_id = json_result['id']
        fname = json_result['name']['givenName']
        lname = json_result['name']['familyName']
        email = json_result['emails'][0]['value']

        template_values = {'fname': fname,
                           'lname': lname,
                           'user_id': user_id}

        result = urlfetch.fetch("https://api.coinmarketcap.com/v1/ticker/?limit=100")
        json_crypto_assests = json.loads(result.content)

        user_CA_exists = False
        user_A_exists = False

        for user in CryptoAsset.query():
            if user.user_id == user_id:
                user_CA_exists = True

        for user in UserAccount.query():
            if user.user_id == user_id:
                user_A_exists = True

        if not user_A_exists:
            new_UA = UserAccount()
            new_UA.user_id = user_id
            new_UA.fname = fname
            new_UA.lname = lname
            new_UA.email = email
            new_UA.put()
            new_UA.id = str(new_UA.key.urlsafe())
            new_UA.put()

        if not user_CA_exists:
            new_CP = CryptoAsset()
            rand_num = randint(0,100)
            new_CP.user_id = user_id
            new_CP.name = json_crypto_assests[rand_num]['name']
            new_CP.symbol = json_crypto_assests[rand_num]['symbol']
            new_CP.rank = json_crypto_assests[rand_num]['rank']
            new_CP.price_usd = json_crypto_assests[rand_num]['price_usd']
            new_CP.put()
            new_CP.id = str(new_CP.key.urlsafe())
            new_CP.put()

        path = os.path.join(os.path.dirname(__file__), 'templates/oauth.html')
        self.response.out.write(template.render(path, template_values))


class UserHandler(webapp2.RequestHandler):
    def get(self, user_id):
        user_exists = False
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
        if user_exists:
            assets_and_account = []
            CryptoAsset_key = ""
            for asset in CryptoAsset.query():
                if asset.user_id == user_id:
                    CryptoAsset_key = asset.id
                    get_CryptoAsset = ndb.Key(urlsafe=CryptoAsset_key).get()
                    get_CryptoAsset_dict = get_CryptoAsset.to_dict()
                    get_CryptoAsset_dict['self'] = "/users/" + user_id + "/cryptoassets/" + asset.id
                    assets_and_account.append(get_CryptoAsset_dict)

            UserAccount_key = ""
            for user in UserAccount.query():
                if user.user_id == user_id:
                    UserAccount_key = user.id

            get_UserAccount = ndb.Key(urlsafe=UserAccount_key).get()
            get_UserAccount_dict = get_UserAccount.to_dict()
            assets_and_account.append(get_UserAccount_dict)

            self_string = "/users/" + user_id
            self_dict = {"self": self_string}
            assets_and_account.append(self_dict)
            self.response.write(json.dumps(assets_and_account))
        else:
            self.response.status = 400
            self.response.write("ERROR: User does not exist")


class CryptoAssetsHandler(webapp2.RequestHandler):
    def get(self, user_id, asset_id=None):
        user_exists = False
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
        if user_exists:
            if asset_id:
                cryptoAsset_exists = False
                for cryptoAsset in CryptoAsset.query():
                    if cryptoAsset.id == asset_id:
                        cryptoAsset_exists = True
                if cryptoAsset_exists:
                    get_CryptoAsset = ndb.Key(urlsafe=asset_id).get()
                    get_CryptoAsset_dict = get_CryptoAsset.to_dict()
                    get_CryptoAsset_dict['self'] = "/users/" + user_id + "/cryptoassets/" + asset_id
                    self.response.write(json.dumps(get_CryptoAsset_dict))
                else:
                    self.response.status = 400
                    self.response.write("ERROR: Crypto Asset does not exist")
            else:
                result = urlfetch.fetch("https://api.coinmarketcap.com/v1/ticker/?limit=100")
                json_crypto_assests = json.loads(result.content)
                asset_total = 0.0
                asset_list = []
                CryptoAsset_key = ""
                for user in CryptoAsset.query():
                    if user.user_id == user_id:
                        CryptoAsset_key = user.id
                        get_CryptoAsset = ndb.Key(urlsafe=CryptoAsset_key).get()
                        get_CryptoAsset_dict = get_CryptoAsset.to_dict()
                        get_CryptoAsset_dict['self'] = "/users/" + user_id + "/cryptoassets/" + user.id
                        asset_list.append(get_CryptoAsset_dict)
                        for i in range(100):
                            if json_crypto_assests[i]['name'] == get_CryptoAsset_dict['name']:
                                asset_total = asset_total + float(json_crypto_assests[i]['price_usd'])
                self_string = "/users/" + user_id + "/cryptoassets"
                self_dict = {"self": self_string}
                asset_list.append(self_dict)
                asset_total_dict = {"asset_total": asset_total}
                asset_list.append(asset_total_dict)
                self.response.write(json.dumps(asset_list))
        else:
            self.response.status = 400
            self.response.write("ERROR: User does not exist")


    def post(self, user_id):
        post_data = json.loads(self.request.body)
        user_exists = False
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
        if user_exists:
            result = urlfetch.fetch("https://api.coinmarketcap.com/v1/ticker/?limit=100")
            json_crypto_assests = json.loads(result.content)
            input_name = False
            asset_found = False
            index = 0
            for item in post_data:
                if item == "name":
                    input_name = True
            if input_name:
                for i in range(100):
                    if json_crypto_assests[i]['name'] == post_data['name']:
                        index = i
                        asset_found = True
                if asset_found:
                    post_cryptoAsset = CryptoAsset()
                    post_cryptoAsset.user_id = user_id
                    post_cryptoAsset.name = json_crypto_assests[index]['name']
                    post_cryptoAsset.symbol = json_crypto_assests[index]['symbol']
                    post_cryptoAsset.rank = json_crypto_assests[index]['rank']
                    post_cryptoAsset.price_usd = json_crypto_assests[index]['price_usd']
                    post_cryptoAsset.put()
                    post_cryptoAsset.id = str(post_cryptoAsset.key.urlsafe())
                    post_cryptoAsset.put()
                    post_cryptoAsset_dict = post_cryptoAsset.to_dict()
                    post_cryptoAsset_dict['self'] = '/users/' + post_cryptoAsset.user_id + "/cryptoassets/" + post_cryptoAsset.id
                    self.response.write(json.dumps(post_cryptoAsset_dict))
                else:
                    self.response.status = 400
                    self.response.write("ERROR: Crypto Asset specified could not be found")
            else:
                self.response.status = 400
                self.response.write("ERROR: expected format -> {\"name\": \"str\"")
        else:
            self.response.status = 400
            self.response.write("ERROR: User does not exist")


    def delete(self, user_id, asset_id):
        user_exists = False
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
        if user_exists:
            cryptoAsset_exists = False
            for cryptoAsset in CryptoAsset.query():
                if cryptoAsset.id == asset_id:
                    cryptoAsset_exists = True
            if cryptoAsset_exists:
                ndb.Key(urlsafe=asset_id).delete()
                self.response.write("SUCCESS: Crypto Asset was deleted")
            else:
                self.response.status = 400
                self.response.write("ERROR: Crypto Asset does not exist")
        else:
            self.response.status = 400
            self.response.write("ERROR: User does not exist")


    def patch(self, user_id, asset_id):
        patch_data = json.loads(self.request.body)
        user_exists = False
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
        if user_exists:
            cryptoAsset_exists = False
            for cryptoAsset in CryptoAsset.query():
                if cryptoAsset.id == asset_id:
                    cryptoAsset_exists = True
            if cryptoAsset_exists:
                patch_cryptoAsset = ndb.Key(urlsafe=asset_id).get()
                if len(patch_data) > 1:
                    self.response.status = 400
                    self.response.write("ERROR: expected format -> {\"name\": \"str\"} or {\"symbol\": \"str\"} or {\"rank\": \"str\"} or {\"price_usd\": \"str\"}")
                else:
                    for key in patch_data:
                        if key == "name":
                            patch_cryptoAsset.name = patch_data['name']
                            patch_cryptoAsset.put()
                            self.response.write("SUCCESS: Crypto Asset 'name' was updated")
                        elif key == "symbol":
                            patch_cryptoAsset.symbol = patch_data['symbol']
                            patch_cryptoAsset.put()
                            self.response.write("SUCCESS: Crypto Asset 'symbol' was updated")
                        elif key == "rank":
                            patch_cryptoAsset.rank = patch_data['rank']
                            patch_cryptoAsset.put()
                            self.response.write("SUCCESS: Crypto Asset 'rank' was updated")
                        elif key == "price_usd":
                            patch_cryptoAsset.price_usd = patch_data['price_usd']
                            patch_cryptoAsset.put()
                            self.response.write("SUCCESS: Crypto Asset 'price_usd' was updated")
                        else:
                            self.response.status = 400
                            self.response.write("ERROR: expected format -> {\"name\": \"str\"} or {\"symbol\": \"str\"} or {\"rank\": \"str\"} or {\"price_usd\": \"str\"}")
            else:
                self.response.status = 400
                self.response.write("ERROR: Crypto Asset does not exist")
        else:
            self.response.status = 400
            self.response.write("ERROR: User does not exist")


    def put(self, user_id, asset_id):
        put_data = json.loads(self.request.body)
        user_exists = False
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_exists = True
        if user_exists:
            cryptoAsset_exists = False
            for cryptoAsset in CryptoAsset.query():
                if cryptoAsset.id == asset_id:
                    cryptoAsset_exists = True
            if cryptoAsset_exists:
                put_cryptoAsset = ndb.Key(urlsafe=asset_id).get()
                input_name = False
                input_symbol = False
                input_rank = False
                input_price_usd = False
                for item in put_data:
                    if item == "name":
                        input_name = True
                    elif item == "symbol":
                        input_symbol = True
                    elif item == "rank":
                        input_rank = True
                    elif item == "price_usd":
                        input_price_usd = True
                if input_name and input_symbol and input_rank and input_price_usd:
                    put_cryptoAsset.name = put_data['name']
                    put_cryptoAsset.symbol = put_data['symbol']
                    put_cryptoAsset.rank = put_data['rank']
                    put_cryptoAsset.price_usd = put_data['price_usd']
                    put_cryptoAsset.put()
                    self.response.write("SUCCESS: Crypto Asset 'name', 'symbol', 'rank', and 'price_usd' were updated")
                else:
                    self.response.status = 400
                    self.response.write("ERROR: expected format -> {\"name\": \"str\", \"symbol\": \"str\", \"rank\": \"str\", \"price_usd\": \"str\"}")
            else:
                self.response.status = 400
                self.response.write("ERROR: Crypto Asset does not exist")
        else:
            self.response.status = 400
            self.response.write("ERROR: User does not exist")

class UserAccountHandler(webapp2.RequestHandler):
    def get(self, user_id):
        user_account_exists = False
        UserAccount_key = ""
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_account_exists = True
                UserAccount_key = user.id
        if user_account_exists:
            get_UserAccount = ndb.Key(urlsafe=UserAccount_key).get()
            get_UserAccount_dict = get_UserAccount.to_dict()
            get_UserAccount_dict['self'] = "/users/" + user_id + "/accountinfo"
            self.response.write(json.dumps(get_UserAccount_dict))
        else:
            self.response.status = 400
            self.response.write("ERROR: User does not exist")

    def delete(self, user_id):
        user_account_exists = False
        UserAccount_key = ""
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_account_exists = True
                UserAccount_key = user.id
        if user_account_exists:
            ndb.Key(urlsafe=UserAccount_key).delete()
            self.response.write("SUCCESS: User's account was deleted")
        else:
            self.response.status = 400
            self.response.write("ERROR: User does not exist")


    def patch(self, user_id):
        patch_data = json.loads(self.request.body)
        user_account_exists = False
        UserAccount_key = ""
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_account_exists = True
                UserAccount_key = user.id
        if user_account_exists:
            patch_user = ndb.Key(urlsafe=UserAccount_key).get()
            if len(patch_data) > 1:
                self.response.status = 400
                self.response.write("ERROR: expected format -> {\"fname\": \"str\"} or {\"lname\": \"str\"} or {\"email\": \"str\"}")
            else:
                for key in patch_data:
                    if key == "fname":
                        patch_user.fname = patch_data['fname']
                        patch_user.put()
                        self.response.write("SUCCESS: User 'fname' was updated")
                    elif key == "lname":
                        patch_user.lname = patch_data['lname']
                        patch_user.put()
                        self.response.write("SUCCESS: User 'lname' was updated")
                    elif key == "email":
                        patch_user.email = patch_data['email']
                        patch_user.put()
                        self.response.write("SUCCESS: User 'email' was updated")
                    else:
                        self.response.status = 400
                        self.response.write("ERROR: expected format -> {\"fname\": \"str\"} or {\"lname\": \"str\"} or {\"email\": \"str\"}")
        else:
            self.response.status = 400
            self.response.write("ERROR: User does not exist")


    def put(self, user_id):
        put_data = json.loads(self.request.body)
        user_account_exists = False
        UserAccount_key = ""
        for user in UserAccount.query():
            if user.user_id == user_id:
                user_account_exists = True
                UserAccount_key = user.id
        if user_account_exists:
            put_user = ndb.Key(urlsafe=UserAccount_key).get()
            input_fname = False
            input_lname = False
            input_email = False
            for item in put_data:
                if item == "fname":
                    input_fname = True
                elif item == "lname":
                    input_lname = True
                elif item == "email":
                    input_email = True
            if input_fname and input_lname and input_email:
                put_user.fname = put_data['fname']
                put_user.lname = put_data['lname']
                put_user.email = put_data['email']
                put_user.put()
                self.response.write("SUCCESS: User 'fname', 'lname', and 'email' were updated")
            else:
                self.response.status = 400
                self.response.write("ERROR: expected format -> {\"fname\": \"str\", \"lname\": \"str\", \"email\": \"str\"}")
        else:
            self.response.status = 400
            self.response.write("ERROR: User does not exist")

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/oauth',OAuthHandler),
    ('/users/(.*)/cryptoassets/(.*)',CryptoAssetsHandler),
    ('/users/(.*)/cryptoassets',CryptoAssetsHandler),
    ('/users/(.*)/accountinfo',UserAccountHandler),
    ('/users/(.*)',UserHandler)
], debug=True)
