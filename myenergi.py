import requests
from requests.auth import HTTPDigestAuth

hub_serial = <HUB SERIAL HERE>
hub_pwd = <API KEY HERE>
director_url = "https://director.myenergi.net"

def get_charge_state():
    response = requests.get(director_url, auth=HTTPDigestAuth(hub_serial, hub_pwd))
    print(response)
    print(response.headers['X_MYENERGI-asn'])

    # Step 1: Ask the Director for your assigned ASN
    print("Director response:", response)

    asn = response.headers.get("X_MYENERGI-asn")
    print("Assigned ASN:", asn)

    # Step 2: Build correct base URL
    base_url = f"https://{asn}"

    # Step 3: Request Zappi status
    zappi_status_url = f"{base_url}/cgi-jstatus-Z"
    zappi_response = requests.get(zappi_status_url, auth=HTTPDigestAuth(hub_serial, hub_pwd))

    print("Zappi status response:", zappi_response)
    print("'sta' indicates charge state:")
    print("• 1 = Waiting (not charging) • 3 = ECO / ECO+ charging • 4 = Fast charging • 5 = Boost charging")
    print("Zappi JSON:")

    data = zappi_response.json()
    sta = data["zappi"][0]["sta"]
    print("Charging state (sta):", sta)
    return sta