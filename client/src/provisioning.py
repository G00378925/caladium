#
#  provisioning.py
#  caladium
#
#  Created by Declan Kelly on 05-02-2023.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, os, sys, urllib.request

# Returns the path to the Caladium file directory
def get_caladium_appdata_dir():
    if sys.platform == "win32":
        return os.environ["USERPROFILE"] + "{0}AppData{0}Local{0}Caladium".format(os.path.sep)
    elif sys.platform == "darwin": return "/tmp"
    else: return None

def unprovision_caladium(caladium_appdata_dir):
    if os.path.exists(caladium_appdata_dir + os.path.sep + "config.json"):
        os.remove(caladium_appdata_dir + os.path.sep + "config.json")

def get_config():
    return load_config(get_caladium_appdata_dir())

def load_config(caladium_appdata_dir):
    config_json_location = caladium_appdata_dir + os.path.sep + "config.json"

    # If the config file doesn't exist, return None
    if not os.path.exists(config_json_location): return None

    with open(config_json_location) as config_json_handle:
        globals()["config"] = json.load(config_json_handle)
        return globals()["config"]

def save_config(caladium_appdata_dir, config):
    # Encode the config as JSON and save it to the config file
    with open(caladium_appdata_dir + os.path.sep + "config.json", "w") as f:
        f.write(json.dumps(config))

def caladium_api(resource_path, method="GET", data=None):
    config = get_config()
    req_headers = {"Authorisation": config["authorisation_token"]}
    req_obj = urllib.request.Request(f"http://{config['server_address']}{resource_path}", headers=req_headers, data=data, method=method)
    return urllib.request.urlopen(req_obj).read().decode("utf-8")

def test_server_connection(config):
    # Check if the caladium server is running
    try: return caladium_api("/api/tasks/test_connection") == "OK"
    except: return False
