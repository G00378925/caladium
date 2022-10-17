#!/usr/bin/env python3
#
#  __main__.py
#  caladium
#
#  Created by Declan Kelly on 10-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, os, sys, tkinter, tkinter.filedialog
import tkinter.messagebox, tkinter.ttk, urllib.request

import dirchangelistener, quarantine, quarantineframe

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

def main(argv):
    config = load_config(argv)
    caladium_appdata_location = get_caladium_appdata_location()

    quarantine_obj = quarantine.Quarantine(caladium_appdata_location + os.path.sep + "Quarantine")

    def dirchangelistener_callback(file_path):
        print("Change detected:", file_path)

    dirchangelistener_obj = dirchangelistener.DirChangeListener([], dirchangelistener_callback)
    dirchangelistener_obj.start()

    main_window = tkinter.Tk()
    main_window.minsize(640, 480)
    main_window.title("Caladium")

    main_window_notebook = tkinter.ttk.Notebook(main_window)
    main_window_notebook.pack(fill=tkinter.BOTH)

    main_frame = tkinter.ttk.Frame()
    main_window_notebook.add(main_frame, text="Caladium")
    quarantine_frame = quarantineframe.QuarantineFrame(main_window, quarantine_obj)
    main_window_notebook.add(quarantine_frame, text="Quarantine")

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

    upload_file_button = tkinter.Button(main_frame, command=upload_file)
    upload_file_button["text"] = "Upload file"
    upload_file_button.pack()

    main_window.mainloop()

if __name__ == "__main__":
    main(sys.argv)

