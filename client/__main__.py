#!/usr/bin/env python3
#
#  __main__.py
#  caladium
#
#  Created by Declan Kelly on 10-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import tkthread
tkthread.patch()

import base64, json, os, sys, tkinter, tkinter.filedialog
import tkinter.messagebox, tkinter.ttk, urllib

import dirchangelistener, provisioningframe, scanwindow, quarantine, quarantineframe

def scan_file(file_path=None):
    try:
        file_handle = open(file_path, "rb") if file_path else tkinter.filedialog.askopenfile("rb")
        if not hasattr(file_handle, "name"): return
        file_name = file_handle.name.split('/')[-1]
        file_data = base64.b64encode(file_handle.read()).decode("utf-8")
        data = json.dumps({"command": "run", "file-name": file_name, "file-data": file_data}).encode()
        file_handle.close()

        main_window = tkinter.Toplevel()

        scanwindow.ScanWindow(main_window).start(data, globals()["config"])
    except (IsADirectoryError):
        tkinter.messagebox.showerror("Error", "Error opening file")
    except (urllib.error.URLError):
        tkinter.messagebox.showerror("Error", "Error establishing connection to server")

def get_caladium_appdata_dir():
    if sys.platform == "win32": return os.environ["USERPROFILE"] + "{0}AppData{0}Local{0}Caladium".format(os.path.sep)
    elif sys.platform == "darwin": return "/tmp"
    else: return None

def get_downloads_dir():
    return (os.environ["USERPROFILE"] if sys.platform == "win32" else os.environ["HOME"]) + "{0}Downloads".format(os.path.sep)

def provisioning_complete(config, main_window):
    globals()["config"], globals()["main_window"] = config, main_window
    quarantine_obj = quarantine.Quarantine(get_caladium_appdata_dir() + os.path.sep + "Quarantine")

    main_window_notebook = tkinter.ttk.Notebook(main_window)
    main_window_notebook.pack(fill=tkinter.BOTH)

    main_frame = tkinter.ttk.Frame()
    main_window_notebook.add(main_frame, text="Caladium")
    quarantine_frame = quarantineframe.QuarantineFrame(main_window, quarantine_obj)
    main_window_notebook.add(quarantine_frame, text="Quarantine")

    upload_file_button = tkinter.Button(main_frame, command=scan_file)
    upload_file_button["text"] = "Scan file"
    upload_file_button.pack()

    def dirchangelistener_callback(file_path):
        @tkthread.main(main_window)
        def scan_file_thread():
            if tkinter.messagebox.askyesno("New file detected " + file_path, file_path):
                scan_file(file_path)

    downloads_dir_location = get_downloads_dir()
    dirchangelistener_obj = dirchangelistener.DirChangeListener([downloads_dir_location], dirchangelistener_callback, main_window)
    dirchangelistener_obj.start()

def main(argv):
    main_window = tkinter.Tk()
    main_window.minsize(640, 480)
    main_window.title("Caladium")

    def kill_client():
        if tkinter.messagebox.askokcancel("Quit", "Do you want to kill the client?"):
            main_window.destroy()
            sys.exit(0)
    main_window.protocol("WM_DELETE_WINDOW", kill_client)

    globals()["main_window"] = main_window

    provisioning_frame = provisioningframe.ProvisioningFrame(main_window, provisioning_complete, get_caladium_appdata_dir())
    provisioning_frame.pack(fill=tkinter.BOTH)
    provisioning_frame.provision(argv[0] if len(argv) > 0 else None)

    main_window.mainloop()

if __name__ == "__main__":
    main(sys.argv[1:])

