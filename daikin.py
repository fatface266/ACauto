import http.server
import socketserver
import threading
import webbrowser
import requests
import urllib.parse
import http.client
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
import subprocess
import json



CLIENT_ID = <CLIENT ID HERE>
CLIENT_SECRET = <CLIENT SECRET CODE HERE>
REDIRECT_URI = <CLIENT REDIRECT URL HERE>

AUTH_URL = "https://idp.onecta.daikineurope.com/v1/oidc/authorize"
TOKEN_URL = "https://idp.onecta.daikineurope.com/v1/oidc/token?"
API_URL = "https://api.onecta.daikineurope.com"

SCOPE = "openid onecta:basic.integration"

auth_code = None


def build_auth_url():
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE
    }

    encoded = urllib.parse.urlencode(params, quote_via=urllib.parse.quote)
    full_url = f"{AUTH_URL}?{encoded}"
    return full_url

def get_tokens(auth_code):
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    r = requests.post(TOKEN_URL, data=data)
    r.raise_for_status()
    return r.json()


def request_state(access_token):
    conn = http.client.HTTPSConnection("api.onecta.daikineurope.com")
    headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
    }
    conn.request("GET", "/v1/gateway-devices/<GATEWAY ID HERE>", headers=headers)

    res = conn.getresponse()
    data = res.read()
    decoded = data.decode("utf-8")
    parsed = json.loads(decoded)
    return parsed

def extension_ac_onoff(access_token, pwr):
    conn = http.client.HTTPSConnection("api.onecta.daikineurope.com")
    headers = {"Authorization": f"Bearer {access_token}","Accept": "*/*",'Content-Type': "application/json"}
    payload = json.dumps({"value": pwr})
    conn.request("PATCH", "/v1/gateway-devices/<GATEWAY ID HERE>/management-points/climateControl/characteristics/onOffMode", payload, headers)
    
    res = conn.getresponse()
    data = res.read()

    print(data.decode("utf-8"))
    if pwr == "on":
        print("Extension AC set to on")
    if pwr == "off":
        print("Extension AC set to off")
    else:
        raise Exception("unknown state")


def start_tunnel():
    process = subprocess.Popen(
        ["cloudflared", "tunnel", "run", "<TUNNEL NAME HERE>"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        parsed = urlparse.urlparse(self.path)
        params = urlparse.parse_qs(parsed.query)

        auth_code = params.get("code", [None])[0]
        #state = params.get("state", [None])[0]

        print("Received code:", auth_code)
        #print("State:", state)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"You can close this window now.")
        return auth_code



def authorise():

    tunnel_process = start_tunnel()
    start_tunnel()
    
    url = build_auth_url()
    print("Authorization URL:")
    print(url)

    print("Opening browser for login…")
    webbrowser.open(url)

    server = HTTPServer(("localhost", 5000), Handler)
    print("Listening on http://localhost:5000 ...")
    server.handle_request()

    print("Authorization code received! Exchanging for tokens…")
    print(auth_code)
    tokens = get_tokens(auth_code)

    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token")

    print("Access Token:", access_token[:40], "…")
    print("Refresh Token:", refresh_token[:40], "…")
    return access_token, refresh_token

def token_refresh(refresh_token):

    url = build_auth_url()
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": refresh_token        
    }
    r = requests.post(TOKEN_URL, data=data)
    r.raise_for_status()
    tokens = r.json()
    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token")
    print("Access Token:", access_token[:40], "…")
    print("Refresh Token:", refresh_token[:40], "…")
    return access_token, refresh_token


def is_ac_on(access_token):
    data = request_state(access_token)
    # Find the climateControl block
    for mp in data["managementPoints"]:
        if mp["embeddedId"] == "climateControl":
            onoff = mp["onOffMode"]["value"]
            print("onOffMode =", onoff)
            return onoff

















