#
#  scanwindow.py
#  caladium
#
#  Created by Declan Kelly on 09-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import json, tkinter, tkinter.scrolledtext, tkinter.ttk, urllib.request

import tkthread

class ScanWindow:
    def __init__(self, main_window):
        self.main_window = main_window
        self.window_handle = tkinter.Toplevel(main_window)

        self.scrolled_text = tkinter.scrolledtext.ScrolledText(self.window_handle)
        self.scrolled_text.grid(row=0, column=0, columnspan=2)
        self.scrolled_text["state"] = "disabled"

        self.progress_bar = tkinter.ttk.Progressbar(self.window_handle)
        self.progress_bar.grid(row=1, column=0, columnspan=2)

    def display_update(self, update_obj):
        match update_obj["type"]:
            case "message":
                self.scrolled_text["state"] = "normal"
                self.scrolled_text.insert(tkinter.CURRENT, update_obj["text"] + '\n')
                self.scrolled_text["state"] = "disabled"
            case "progress":
                self.progress_bar["value"] = update_obj["value"]

    def scan_file(self):
        data, config = globals()["data"], globals()["config"]

        req_url = f"http://{config['server_address']}/api/tasks"
        req_headers = {"Authorisation": config["authorisation_token"]}
        req_obj = urllib.request.Request(req_url, data=data, headers=req_headers, method="POST")
        try: resp_obj = json.loads(urllib.request.urlopen(req_obj).read().decode("utf-8"))
        except: ...

        message_count = 0

        while True:
            req_url = f"http://{config['server_address']}/api/tasks/{resp_obj['_id']}"
            req_obj = urllib.request.Request(req_url, data=data, headers=req_headers, method="GET")
            try: resp_obj = json.loads(urllib.request.urlopen(req_obj).read().decode("utf-8"))
            except: ...

            if len(resp_obj["updates"]) > message_count:
                [self.display_update(update) for update in resp_obj["updates"][message_count:]]
                message_count = len(resp_obj["updates"])

            self.main_window.update()
            self.main_window.after(100)

    def start(self, data, config):
        globals()["data"], globals()["config"] = data, config

        @tkthread.main(self.main_window)
        def start_thread():
            self.scan_file()

