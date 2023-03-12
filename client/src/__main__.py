#!/usr/bin/env python3
#
#  __main__.py
#  caladium
#
#  Created by Declan Kelly on 10-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import tkthread
tkthread.patch() # Patch tkinter to allow async operations

import base64, json, os, sys, tkinter

import dirchangelistener, preferencesframe, provisioning, provisioningframe
import quarantine, quarantineframe, scanwindow

# Called when the "Scan File" button is pressed
def scan_file(main_window, quarantine_obj, quarantine_frame, file_path=None):
    try:
        file_handle = open(file_path, "rb") if file_path else tkinter.filedialog.askopenfile("rb")
        if not hasattr(file_handle, "name"): return

        # Encode file data as base64 to be sent to server
        # As raw bytes cannot be stored in JSON
        file_path = file_handle.name
        file_name = file_path.split('/')[-1]

        file_data = base64.b64encode(file_handle.read()).decode("utf-8")
        file_data = json.dumps({"command": "run", "file-name": file_name, "file-data": file_data}).encode()
        file_handle.close()

        def malware_detected_callback(file_path):
            # Ask the user if they want to quarantine the file
            if tkinter.messagebox.askyesno("Do you wish to quarantine?", "Malware detected in file " + file_name):
                quarantine_obj.quarantine_file(file_path)
                quarantine_frame.update_quarantine_list()

        scanwindow.ScanWindow(main_window, malware_detected_callback).start(file_path, file_data)
    except (IsADirectoryError):
        tkinter.messagebox.showerror("Error", "Error opening file")
    except (FileNotFoundError):
        tkinter.messagebox.showerror("Error", "File not found")

def setup_notebook(config, main_window):
    quarantine_obj = quarantine.Quarantine(provisioning.get_caladium_appdata_dir() + os.path.sep + "Quarantine")

    # Each frame is stored as a tab in the main window
    main_window_notebook = tkinter.ttk.Notebook(main_window)
    main_window_notebook.pack(fill=tkinter.BOTH, expand=True, anchor=tkinter.NW)

    # Adding the main frame
    main_frame = tkinter.ttk.Frame()
    main_window_notebook.add(main_frame, text="Caladium")

    # Scanning directory label
    scanning_directory_label = tkinter.ttk.Label(main_frame)
    scanning_directory_label.pack()
    def update_scan_dir_label(scan_dir_path):
        scanning_directory_label["text"] = f"Currently scanning: {scan_dir_path}"

    # Adding the scan file button to the main frame
    upload_file_button = tkinter.Button(main_frame, \
        command=lambda: scan_file(main_window, quarantine_obj, quarantine_frame))
    upload_file_button["text"] = "Scan file"
    upload_file_button.pack()

    # Adding the quarantine frame
    quarantine_frame = quarantineframe.QuarantineFrame(main_window, quarantine_obj)
    main_window_notebook.add(quarantine_frame, text="Quarantine")

    # Adding the preferences frame
    preferences_frame = preferencesframe.PreferencesFrame(main_window)
    main_window_notebook.add(preferences_frame, text="Preferences")

    # Called when a new file is detected in the downloads directory
    def dirchangelistener_callback(file_path):
        @tkthread.main(main_window)
        def scan_file_thread():
            if tkinter.messagebox.askyesno("New file detected " + file_path, file_path):
                scan_file(main_window, quarantine_obj, quarantine_frame, file_path)

    dirchangelistener_obj = dirchangelistener.DirChangeListener(dirchangelistener_callback, main_window, update_scan_dir_label)
    dirchangelistener_obj.start()

def main(argv):
    main_window = tkinter.Tk()
    main_window.minsize(640, 480) # Initially 640x480, this is adjustable
    main_window.title("Caladium")

    # Called when user presses the close button
    def kill_client():
        if tkinter.messagebox.askokcancel("Quit", "Do you want to kill the client?"):
            main_window.destroy()
            os.kill(os.getpid(), 3) # Kill the process

    main_window.protocol("WM_DELETE_WINDOW", kill_client)

    # If the computer isn't already provisioned, show the provisioning frame
    provisioning_frame = provisioningframe.ProvisioningFrame(main_window, setup_notebook, provisioning.get_caladium_appdata_dir())
    provisioning_frame.pack(fill=tkinter.BOTH)
    # Optionally pass a IP address for automatic provisioning
    provisioning_frame.provision(argv[0] if len(argv) > 0 else None)

    main_window.mainloop() # Main loop of execution

if __name__ == "__main__":
    main(sys.argv[1:])
