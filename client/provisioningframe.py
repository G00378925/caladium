#
#  provisioningframe.py
#  caladium
#
#  Created by Declan Kelly on 05-02-2023.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import base64, tkinter, tkinter.filedialog, tkinter.ttk

import provisioning

class ProvisioningFrame(tkinter.ttk.Frame):
    def __init__(self, main_window, provisioning_complete, caladium_appdata_dir):
        super().__init__(main_window)
        self.provisioning_complete = provisioning_complete

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
        ...

