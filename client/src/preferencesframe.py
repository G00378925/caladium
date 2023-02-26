# 02-26-2023 12:31

import os, tkinter.ttk, tkinter.filedialog

import provisioning

class PreferencesFrame(tkinter.ttk.Frame):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.columnconfigure(0, weight=1)
        
        # Widgets to be shown in the preferences frame
        self.preference_items = [
            ["Uninstall Caladium", None],
            ["Change Scanning Directory", None],
            ["Unprovision Caladium", None]
        ]

        # Add the widgets to the list above
        self.preference_items[0][1] = tkinter.ttk.Button(self, command=lambda: self._unistall_caladium())
        self.preference_items[0][1]["text"] = "Uninstall Caladium"

        self.preference_items[1][1] = tkinter.ttk.Button(self, command=lambda: self._change_scanning_directory())
        self.preference_items[1][1]["text"] = "Change Scanning Directory"

        self.preference_items[2][1] = tkinter.ttk.Button(self, command=lambda: self._unprovision_caladium())
        self.preference_items[2][1]["text"] = "Unprovision Caladium"

        # Add the widgets and their label descriptions to the frame
        for i, item in enumerate(self.preference_items):
            label = tkinter.ttk.Label(self)
            label["text"] = item[0]
            label.grid(row=i, column=0, sticky="w")

            widget = item[1]
            widget.grid(row=i, column=1, sticky="e")

    # Called upon the uninstall button being pressed
    def _uninstall_caladium(self):
        print("Uninstall Caladium")

    # Called upon the change scanning directory button being pressed
    def _change_scanning_directory(self):
        if new_directory := tkinter.filedialog.askdirectory():
            globals()["config"] = provisioning.get_config()
            globals()["config"]["scanning_directory"] = new_directory
            provisioning.save_config(provisioning.get_caladium_appdata_dir(), globals()["config"])

    # Called upon the unprovision button being pressed
    def _unprovision_caladium(self):
        provisioning.unprovision_caladium(provisioning.get_caladium_appdata_dir())
        self.main_window.destroy()
        os.kill(os.getpid(), 3)

