import json
import flask
import requests

app = flask.Flask(__name__)

CLIENT_ID = '913425740949-0c0i284ks9elrosgpv5rdh2qvsal8cim.apps.googleusercontent.com'
CLIENT_SECRET = 'tKkgsZh6HK2zWcNeOrlE9kH3'
REDIRECT_URI = 'http://localhost:8080/oauth'

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/oauth')
def oauth():
    auth_code = flask.request.args.get('code')
    data = {'code': auth_code,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'grant_type': 'authorization_code'}

    r = requests.post('https://www.googleapis.com/oauth2/v4/token', data=data)
    credendtials = json.loads(r.text)

    headers = {'Authorization': 'Bearer ' + credendtials['access_token']}
    req_uri = 'https://www.googleapis.com/plus/v1/people/me'
    r = requests.get(req_uri, headers=headers)
    content = json.loads(r.text)

    fname = content.name['givenName']
    lname = content.name['familyName']
    gplink = content.url

    return flask.render_template('oauth.html',
            fname=fname,
            lname=lname,
            gplink=gplink,
            state=CLIENT_SECRET)
