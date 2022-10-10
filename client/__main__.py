#!/usr/bin/env python3
#
#  __main__.py
#  caladium
#
#  Created by Declan Kelly on 10-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, os, sys, tkinter
import tkinter.filedialog, tkinter.messagebox, urllib.request

def load_config(argv):
    config_json_location = ''.join(argv[0].split(os.path.sep)[:-1]) + os.path.sep + "config.json"
    with open(config_json_location) as config_json_handle:
        return json.loads(config_json_handle.read())

def main(argv):
    config = load_config(argv)

    main_window = tkinter.Tk()
    main_window.minsize(640, 480)
    main_window.title("Caladium")

    def upload_file():
        try:
            file_handle = tkinter.filedialog.askopenfile("rb")
            file_data = file_handle.read()
            file_handle.close()

            req_url = f"http://{config['server_address']}/api/upload_file"
            req_headers = {"Authorisation": config["authorisation_token"]}
            req_obj = urllib.request.Request(req_url, data=file_data, headers=req_headers, method="POST")

            resp_obj = urllib.request.urlopen(req_obj)
        except (IsADirectoryError):
            tkinter.messagebox.showerror("Error", "Error opening file")
        except (urllib.error.URLError):
            tkinter.messagebox.showerror("Error", "Error establishing connection to server")

    upload_file_button = tkinter.Button(main_window, command=upload_file)
    upload_file_button["text"] = "Upload file"
    upload_file_button.pack()

    main_window.mainloop()

if __name__ == "__main__":
    main(sys.argv)

