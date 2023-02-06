#
#  provisioning.py
#  caladium
#
#  Created by Declan Kelly on 05-02-2023.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, os, urllib.request

def load_config(caladium_appdata_dir):
    config_json_location = caladium_appdata_dir + os.path.sep + "config.json"

    if not os.path.exists(config_json_location): return None

    with open(config_json_location) as config_json_handle:
        return json.load(config_json_handle)

def save_config(caladium_appdata_dir, config):
    with open(caladium_appdata_dir + os.path.sep + "config.json", "w") as f:
        f.write(json.dumps(config))

def test_server_connection(config):
    try:
        req_headers = {"Authorisation": config["authorisation_token"]}
        req_obj = urllib.request.Request(f"http://{config['server_address']}/api/tasks/test_connection", headers=req_headers)
        return urllib.request.urlopen(req_obj).read().decode("utf-8") == "OK"
    except: return False

