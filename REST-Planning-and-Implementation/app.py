from google.appengine.ext import ndb
import webapp2
import json
import types

class Boat(ndb.Model):
    id = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=True)
    length = ndb.IntegerProperty(required=True)
    at_sea = ndb.BooleanProperty(required=True)

class BoatHandler(webapp2.RequestHandler):
    def post(self):
        post_boat_data = json.loads(self.request.body)
        post_boat = Boat(name=post_boat_data['name'],
                        type=post_boat_data['type'],
                        length=post_boat_data['length'],
                        at_sea=post_boat_data['at_sea'])

        if post_boat.at_sea:
            post_boat.at_sea = false

        post_boat.put()
        post_boat.id = str(post_boat.key.urlsafe())
        post_boat.put()
        post_boat_dict = post_boat.to_dict()
        post_boat_dict['self'] = '/boats/' + post_boat.key.urlsafe()
        self.response.write(json.dumps(post_boat_dict))

    def get(self, id=None):
        if id:
            get_boat = ndb.Key(urlsafe=id).get()
            get_boat_dict= get_boat.to_dict()
            get_boat_dict['self'] = "/boats/" + id
            self.response.write(json.dumps(get_boat_dict))
        else:
            get_boat_query_results = [get_boat_query.to_dict()
                                      for get_boat_query in Boat.query()]

            for boat in get_boat_query_results:
                boat['self'] = "/boats/" + boat['id']

            self.response.write(json.dumps(get_boat_query_results))

    def delete(self, id=None):
        if id:
            slip_boat_is_in = Slip.query(Slip.current_boat == id)
            slip_boat_is_in.current_boat = ""
            slip_boat_is_in.arrival_date = ""
            slip_boat_is_in.put()
            ndb.Key(urlsafe=id).delete()
            self.response.write("boat was deleted")

    def patch(self, id=None):
        if id:
            patch_boat_data = json.loads(self.request.body)
            patch_boat = ndb.Key(urlsafe=id).get()

            if len(patch_boat_data) > 1:
                self.response.write("can only change one item")
            else:
                for key in patch_boat_data:
                    if key == "name":
                        patch_boat.name = patch_boat_data['name']
                        self.response.write("boat name was updated")
                    elif key == "type":
                        patch_boat.type = patch_boat_data['type']
                        self.response.write("boat type was updated")
                    elif key == "length":
                        patch_boat.length = patch_boat_data['length']
                        self.response.write("boat length was updated")
                    else:
                        self.response.write("boat name, type and length can only be edited by a PATCH")
                patch_boat.put()

    def put(self, id=None):
        if id:
            put_boat_data = json.loads(self.request.body)
            if len(put_boat_data) < 3:
                self.response.write("name, type and length should be in body")
            else:
                put_boat = ndb.Key(urlsafe=id).get()
                put_boat.name = put_boat_data['name']
                put_boat.type = put_boat_data['type']
                put_boat.length = put_boat_data['length']
                put_boat.put()
                self.response.write("boat was updated")

class Slip(ndb.Model):
    id = ndb.StringProperty()
    number = ndb.IntegerProperty(required=True)
    current_boat = ndb.StringProperty(required=True)
    arrival_date = ndb.StringProperty(required=True)

class SlipHandler(webapp2.RequestHandler):
    def post(self):
        post_slip_data = json.loads(self.request.body)

        post_slip_query_results = [post_slip_query.to_dict()
                                  for post_slip_query in Slip.query()]
        found_it = 0
        for slip in post_slip_query_results:
            if slip['number'] == post_slip_data['number']:
                found_it = 1
                self.response.write("sorry, that slot number is already taken")
        if not found_it:
            post_slip = Slip(number=post_slip_data['number'],
                            current_boat=post_slip_data['current_boat'],
                            arrival_date=post_slip_data['arrival_date'])
            if post_slip.current_boat:
                post_slip.current_boat = ""

            if post_slip.arrival_date:
                post_slip.arrival_date = ""

            post_slip.put()
            post_slip.id = str(post_slip.key.urlsafe())
            post_slip.put()
            post_slip_dict = post_slip.to_dict()
            post_slip_dict['self'] = '/slips/' + post_slip.key.urlsafe()
            self.response.write(json.dumps(post_slip_dict))

    def get(self, id=None):
        if id:
            get_slip = ndb.Key(urlsafe=id).get()
            get_slip_dict= get_slip.to_dict()
            get_slip_dict['self'] = "/slips/" + id
            self.response.write(json.dumps(get_slip_dict))
        else:
            get_slip_query_results = [get_slip_query.to_dict()
                                      for get_slip_query in Slip.query()]

            for slip in get_slip_query_results:
                slip['self'] = "/slips/" + slip['id']

            self.response.write(json.dumps(get_slip_query_results))

    def delete(self, id=None):
        if id:
            delete_slip = ndb.Key(urlsafe=id).get()
            boat_in_the_slip = ndb.Key(urlsafe=delete_slip.current_boat).get()
            delete_slip.key.delete()
            boat_in_the_slip.at_sea = True;
            boat_in_the_slip.put()
            self.response.write("slip was deleted")

    def patch(self, id=None):
        if id:
            patch_slip_data = json.loads(self.request.body)
            patch_slip = ndb.Key(urlsafe=id).get()

            if len(patch_slip_data) > 1:
                self.response.write("can only change one item")
            else:
                for key in patch_slip_data:
                    if key == "number":
                        patch_slip_query_results = [patch_slip_query.to_dict()
                                                  for patch_slip_query in Slip.query()]
                        found_it = 0
                        for slip in patch_slip_query_results:
                            if slip['number'] == patch_slip_data['number']:
                                found_it = 1
                                self.response.write("sorry, that slot number is already taken")
                        if not found_it:
                            patch_slip.number = patch_slip_data['number']
                            self.response.write("slip number was updated")

                patch_slip.put()

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.write("Welcome to the Marina!")

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boats',BoatHandler),
    ('/boats/(.*)',BoatHandler),
    ('/slips',SlipHandler),
    #('/slips/(.*)/boat',BoatInSlipHandler),
    ('/slips/(.*)',SlipHandler)
], debug=True)
