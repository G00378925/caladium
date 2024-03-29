#
#  scanwindow.py
#  caladium
#
#  Created by Declan Kelly on 09-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import json, tkinter, tkinter.scrolledtext

import tkthread

import provisioning

class ScanWindow:
    def __init__(self, main_window, malware_callback):
        self.main_window = main_window
        self.malware_callback = malware_callback

        # This is the handle for the scanning window
        self.window_handle = tkinter.Toplevel(main_window)
        self.window_handle.title("Scan in progress . . .")
        self.window_handle.protocol("WM_DELETE_WINDOW", lambda: self._stop_scan())

        # This is the log box for the scan
        self.scrolled_text = tkinter.scrolledtext.ScrolledText(self.window_handle)
        self.scrolled_text["state"] = "disabled"
        self.scrolled_text.pack(fill=tkinter.BOTH, expand=True)

        # Progress bar 0 -> 100
        self.progress_bar = tkinter.ttk.Progressbar(self.window_handle)
        self.progress_bar.pack()

        self.current_log_text = str() # Logbox is empty at start
        self.stop_scan = False # Used to stop the scan thread
        self.scan_in_progress = False

    def _display_update(self, update_obj):
        # Handles messages from analysis worker
        match (update_obj["state"] if update_obj["type"] == "state" else update_obj["type"]):
            case "message":
                self.scrolled_text["state"] = "normal" # Allow text to be edited
                self.current_log_text += update_obj["text"] + "\n"

                # Update the text log box
                self.scrolled_text.delete("1.0", "end")
                self.scrolled_text.insert("1.0", self.current_log_text)

                self.scrolled_text["state"] = "disabled" # Disable editing
            case "progress":
                # Update the progress bar
                self.progress_bar["value"] = update_obj["value"]
            case "complete":
                tkinter.messagebox.showinfo("Scan complete", "The scan has completed.")
                self._stop_scan()
            case "malware_detected":
                # When malware is detected, the user is prompted to quarantine the file
                malware_callback = self.malware_callback
                malware_callback(self.file_path)
                self._stop_scan() # No need to continue scanning

    # Small abstraction over tkinter's messagebox
    def _show_error(self, error_message):
        tkinter.messagebox.showerror("Error", error_message, parent=self.window_handle)

    def _scan_file(self, file_data):
        try:
            resp_obj = provisioning.caladium_api("/api/tasks", method="POST", data=file_data, timeout=20)
            self.scan_in_progress = True
            self.task_id = json.loads(resp_obj)["_id"]
        except:
            # Exception when creating task
            self._show_error("An error occurred when establishing a connection to the server.")
            self.window_handle.destroy() # Close the window and return
            return

        message_count = 0 # Amount of messages received

        # Loop, until its no longer scanning
        while not self.stop_scan:
            try:
                resp_obj = json.loads(provisioning.caladium_api(f"/api/tasks/{self.task_id}"))
            except:
                self._show_error("An error occurred when establishing a connection to the server.")
                self.window_handle.destroy() # Close the window and return
                return
            
            # Check if there are any new messages
            if len(resp_obj["updates"]) > message_count:
                [self._display_update(update) for update in resp_obj["updates"][message_count:]]
                message_count = len(resp_obj["updates"])

            # Allow UI to update
            self.main_window.update()
            self.main_window.after(100)

    def _stop_scan(self):
        if self.scan_in_progress:
            self.stop_scan = True # Stop the scan loop
            self.window_handle.destroy() # Kill this window

    def start(self, file_path, file_data):
        self.file_path = file_path

        # tkthread, to allow the UI to not lock up
        @tkthread.main(self.main_window)
        def start_thread(): self._scan_file(file_data)
