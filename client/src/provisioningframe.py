#
#  provisioningframe.py
#  caladium
#
#  Created by Declan Kelly on 05-02-2023.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import base64, json, tkinter

import provisioning

class ProvisioningFrame(tkinter.ttk.Frame):
    def __init__(self, main_window, provisioning_complete, caladium_appdata_dir):
        super().__init__(main_window)
        self.main_window = main_window
        self.provisioning_complete, self.caladium_appdata_dir = provisioning_complete, caladium_appdata_dir

        # Adding widgets for the user to enter their token
        self.token_entry_box = tkinter.Entry(self)
        self.token_entry_box.pack()

        # Adding a button to provision the token
        self.provision_button = tkinter.Button(self, command=lambda: self._provision_token())
        self.provision_button["text"] = "Provision"
        self.provision_button.pack()

    def provision(self, server_address):
        if server_address:
            provisioning.set_preference("server_address", server_address)

            # If auto-provisioning is enabled, request a token from the server
            try:
                req_obj = json.loads(provisioning.caladium_api("/api/auto_provision", method="POST", timeout=5))
                provisioning.set_preference("authorisation_token", req_obj["_id"])
            except:
                tkinter.messagebox.showerror("Error", "Problem occurred during auto-provision")

        # If the authorisation token is in the config, test the connection
        config = provisioning.load_config(self.caladium_appdata_dir)
        if "authorisation_token" in config:
            # If it doesn't work, delete it and ask the user to provision again
            if provisioning.test_server_connection(provisioning.get_config()):
                self.pack_forget()
                self.provisioning_complete(self.main_window)

    def _provision_token(self):
        try:
            token_obj = json.loads(base64.b64decode(self.token_entry_box.get()).decode("utf-8"))
            provisioning.save_config(self.caladium_appdata_dir, token_obj)

            if provisioning.test_server_connection(provisioning.get_config()):
                self.pack_forget()
                self.provisioning_complete(self.main_window)
        except:
            tkinter.messagebox.showerror("Error", "Provision token is malformed.")

