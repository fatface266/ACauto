import http.client
import requests
from requests.auth import HTTPDigestAuth
import time
import json
from daikin import *
from myenergi import *
from datetime import datetime

#run ddaikin Oauth
access_token, refresh_token = authorise()
previous_state = None

while True:
    state = get_charge_state()

    #if previous_state is not None:
    if state != previous_state:
        print(f"State changed! Previous: {previous_state}, Now: {state}")
        if state == 5:
            print("Charging — doing charging action...")
            # do your “charging” behaviour here
            onoff = is_ac_on(access_token)
            if onoff == "off":
                    extension_ac_onoff(access_token, "on")
                    access_token, refresh_token = token_refresh(refresh_token)
            else:
                    access_token, refresh_token = token_refresh(refresh_token)
        
        else:
            print("Not charging — doing alternative action...")
            # do your “not charging” behaviour here
            onoff = is_ac_on(access_token)
            if onoff == "on":
                extension_ac_onoff(access_token, "off")
                access_token, refresh_token = token_refresh(refresh_token)
            else:
                access_token, refresh_token = token_refresh(refresh_token)
    else:
        print(f"State unchanged: {state}")

        
    # wait 5 minutes (300 seconds)
    previous_state = state
    now = datetime.now()
    print(f"time now is {now.strftime('%H:%M:%S')}")
    print("recheck in 5 minutes")
    time.sleep(300)

