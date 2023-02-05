#
#  provisioning.py
#  caladium
#
#  Created by Declan Kelly on 05-02-2023.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import urllib.request

def get_caladium_appdata_location():
    if sys.platform == "win32":
        return os.environ["USERPROFILE"] + "{0}AppData{0}Local{0}Caladium".format(os.path.sep)
    elif sys.platform == "darwin":
        return "/tmp"
    else:
        return None

def load_config(argv):
    config_json_location = ''.join(argv[0].split(os.path.sep)[:-1]) + os.path.sep + "config.json"

    if sys.platform == "win32":
        config_json_location = config_json_location.lstrip(os.path.sep)

    with open(config_json_location) as config_json_handle:
        return json.load(config_json_handle)

