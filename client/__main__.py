#!/usr/bin/env python3
#
#  __main__.py
#  caladium
#
#  Created by Declan Kelly on 10-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import base64, json, os, sys, tkinter, tkinter.filedialog
import tkinter.messagebox, tkinter.ttk, threading, urllib

import dirchangelistener, provisioningframe, scanwindow, quarantine, quarantineframe

def provisioning_complete():
    main_window = globals()["main_window"]
    main_window_notebook = tkinter.ttk.Notebook(main_window)
    main_window_notebook.pack(fill=tkinter.BOTH)

    main_frame = tkinter.ttk.Frame()
    main_window_notebook.add(main_frame, text="Caladium")
    quarantine_frame = quarantineframe.QuarantineFrame(main_window, quarantine_obj)
    main_window_notebook.add(quarantine_frame, text="Quarantine")

    def upload_file():
        try:
            file_handle = tkinter.filedialog.askopenfile("rb")
            file_name = file_handle.name.split('/')[-1]
            file_data = base64.b64encode(file_handle.read()).decode("utf-8")
            data = json.dumps({"command": "run", "file-name": file_name, "file-data": file_data}).encode()
            file_handle.close()

            scanwindow.ScanWindow(main_window).start(data, config)
        except (IsADirectoryError):
            tkinter.messagebox.showerror("Error", "Error opening file")
        except (urllib.error.URLError):
            tkinter.messagebox.showerror("Error", "Error establishing connection to server")

    upload_file_button = tkinter.Button(main_frame, command=upload_file)
    upload_file_button["text"] = "Scan file"
    upload_file_button.pack()

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
    globals()["main_window"] = main_window

    provisioning_frame = provisioningframe.ProvisioningFrame(main_window, provisioning_complete)
    provisioning_frame.pack(fill=tkinter.BOTH)

    main_window.mainloop()

if __name__ == "__main__":
    main(sys.argv)

