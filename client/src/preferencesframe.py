# 02-26-2023 12:31

import ctypes, os, tkinter.ttk, tkinter.filedialog

import provisioning

def __uninstall_caladium():
    uninstallation_code = """
    @echo off
    rem Waiting 3 seconds until Caladium is closed
    timeout /t 3 /nobreak > nul

    rd /S /Q "{0}"

    rem Delete the Caladium shortcut from the users desktop
    del "%USERPROFILE%\\Desktop\\Caladium.lnk"

    rem Deleting start up folder entry
    del "%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\\Caladium.lnk"

    exit
    """.format(os.environ["ProgramFiles"] + os.path.sep + "Caladium")
    batch_file_path = os.environ["TMP"] + os.path.sep + "uninstall.bat"

    # Write the batch code to a file
    with open(batch_file_path, "w") as batch_file:
        batch_file.write(uninstallation_code)

    os.system("start " + batch_file_path) # Execute the batch file

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
        self.preference_items[0][1] = tkinter.ttk.Button(self, command=lambda: self._uninstall_caladium())
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
        # Check if the user is running as admin
        if not ctypes.windll.shell32.IsUserAnAdmin():
            tkinter.messagebox.showerror("Error", "Caladium must be running as administrator to uninstall")
            return

        if tkinter.messagebox.askyesno("Uninstall Caladium", "Are you sure you want to uninstall?"):
            __uninstall_caladium() # Uninstall Caladium
            os.kill(os.getpid(), 3) # Kill the process

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

