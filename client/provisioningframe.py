#
#  provisioningframe.py
#  caladium
#
#  Created by Declan Kelly on 05-02-2023.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import base64, json, tkinter, tkinter.filedialog, tkinter.ttk

import provisioning

class ProvisioningFrame(tkinter.ttk.Frame):
    def __init__(self, main_window, provisioning_complete, caladium_appdata_dir):
        super().__init__(main_window)
        self.provisioning_complete, self.caladium_appdata_dir = provisioning_complete, caladium_appdata_dir

        self.token_entry_box = tkinter.Entry(self)
        self.token_entry_box.pack()

        self.provision_button = tkinter.Button(self, command=lambda: self._provision_token())
        self.provision_button["text"] = "Provision"
        self.provision_button.pack()

        globals()["config"] = provisioning.load_config(caladium_appdata_dir)
        if globals()["config"]:
            if provisioning.test_server_connection(globals()["config"]):
                provisioning_complete()

    def _provision_token(self):
        try:
            token_obj = json.loads(base64.b64decode(self.token_entry_box["text"]).decode("utf-8"))
            provisioning.save_config(self.caladium_appdata_dir, token_obj)

            globals()["config"] = provisioning.load_config(caladium_appdata_dir)
            if provisioning.test_server_connection(globals()["config"]):
                self.provisioning_complete()
        except (json.decoder.JSONDecodeError):
            tkinter.messagebox.showerror("Error", "Provision token is malformed.")

