#
#  setup.py
#  caladium
#
#  Created by Declan Kelly on 09-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import json, os, sys

import requests

if not os.environ.get("CALADIUM_SERVER_ADDRESS", None):
    sys.stderr.write("CALADIUM_SERVER_ADDRESS environmental variable must be set.")
    sys.exit(0)

CALADIUM_SERVER_ADDRESS = os.environ["CALADIUM_SERVER_ADDRESS"]

def get_http_headers(server_address, username, password):
    headers = {"username": username, "password": password}
    token = json.loads(requests.post(f"http://{server_address}/api/login", headers=headers).text)["Authorisation"]
    return {"Authorisation": token}

