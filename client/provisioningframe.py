#
#  provisioningframe.py
#  caladium
#
#  Created by Declan Kelly on 05-02-2023.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import base64, json, tkinter, tkinter.filedialog, tkinter.ttk, urllib

import provisioning

class ProvisioningFrame(tkinter.ttk.Frame):
    def __init__(self, main_window, provisioning_complete, caladium_appdata_dir):
        super().__init__(main_window)
        self.main_window = main_window
        self.provisioning_complete, self.caladium_appdata_dir = provisioning_complete, caladium_appdata_dir

        self.token_entry_box = tkinter.Entry(self)
        self.token_entry_box.pack()

        self.provision_button = tkinter.Button(self, command=lambda: self._provision_token())
        self.provision_button["text"] = "Provision"
        self.provision_button.pack()

    def provision(self, server_address):
        globals()["config"] = provisioning.load_config(self.caladium_appdata_dir)

        if not globals()["config"] and server_address:
            globals()["config"] = {}

            req_obj = urllib.request.Request(f"http://{server_address}/api/auto_provision", method="POST")
            globals()["config"]["authorisation_token"] = json.loads(urllib.request.urlopen(req_obj).read().decode("utf-8"))["_id"]
            globals()["config"]["server_address"] = server_address

            provisioning.save_config(self.caladium_appdata_dir, globals()["config"])

        if globals()["config"]:
            if provisioning.test_server_connection(globals()["config"]):
                self.pack_forget()
                self.provisioning_complete(globals()["config"], self.main_window)

    def _provision_token(self):
        try:
            token_obj = json.loads(base64.b64decode(self.token_entry_box.get()).decode("utf-8"))
            provisioning.save_config(self.caladium_appdata_dir, token_obj)

            globals()["config"] = provisioning.load_config(self.caladium_appdata_dir)
            if provisioning.test_server_connection(globals()["config"]):
                self.pack_forget()
                self.provisioning_complete(globals()["config"], self.main_window)
        except:
            tkinter.messagebox.showerror("Error", "Provision token is malformed.")

