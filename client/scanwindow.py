#
#  scanwindow.py
#  caladium
#
#  Created by Declan Kelly on 09-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import json, threading, time, tkinter
import tkinter.scrolledtext, tkinter.ttk, urllib.request

class ScanWindow:
    def __init__(self, main_window):
        self.window_handle = tkinter.Toplevel(main_window)

        self.scrolled_text = tkinter.scrolledtext.ScrolledText(self.window_handle)
        self.scrolled_text.grid(row=0, column=0, columnspan=2)

        self.progress_bar = tkinter.ttk.Progressbar(self.window_handle)
        self.progress_bar.grid(row=1, column=0, columnspan=2)

    def scan_file(self):
        data, config = globals()["data"], globals()["config"]

        req_url = f"http://{config['server_address']}/api/tasks"
        req_headers = {"Authorisation": config["authorisation_token"]}
        req_obj = urllib.request.Request(req_url, data=data, headers=req_headers, method="POST")
        resp_obj = json.loads(urllib.request.urlopen(req_obj).read().decode("utf-8"))

        while True:
            req_url = f"http://{config['server_address']}/api/tasks/{resp_obj['_id']}"
            req_obj = urllib.request.Request(req_url, data=data, headers=req_headers, method="GET")
            resp_obj = json.loads(urllib.request.urlopen(req_obj).read().decode("utf-8"))

            self.scrolled_text.insert(tkinter.CURRENT, f"{resp_obj}\n")
            time.sleep(1)

    def start(self, data, config):
        globals()["data"], globals()["config"] = data, config

        threading.Thread(target=self.scan_file).start()
        self.window_handle.mainloop()

