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
    def __init__(self, main_window):
        # This is the handle for the scanning window
        self.window_handle = tkinter.Toplevel(main_window)
        self.window_handle.title("Scanning in progress . . .")
        self.window_handle.protocol("WM_DELETE_WINDOW", lambda: self._stop_scan())

        self.scrolled_text = tkinter.scrolledtext.ScrolledText(self.window_handle)
        self.scrolled_text.grid(row=0, column=0, columnspan=2)
        self.scrolled_text["state"] = "disabled"

        self.progress_bar = tkinter.ttk.Progressbar(self.window_handle)
        self.progress_bar.grid(row=1, column=0, columnspan=2)

        self.current_log_text = str()
        self.stop_scan = False # Used to stop the scan thread
        self.scan_in_progress = False

    def _display_update(self, update_obj):
        match update_obj["type"]:
            case "message":
                self.scrolled_text["state"] = "normal"
                self.current_log_text += update_obj["text"] + "\n"

                # Update the text log box
                self.scrolled_text.delete("1.0", "end")
                self.scrolled_text.insert("1.0", self.current_log_text)

                self.scrolled_text["state"] = "disabled"
            case "progress":
                self.progress_bar["value"] = update_obj["value"]

    def _scan_file(self, data, config):
        try:
            resp_obj = provisioning.caladium_api("/api/tasks", method="POST", data=data)
            self.scan_in_progress = True
            self.task_id = json.loads(resp_obj)["_id"]
        except:
            # Exception when creating task
            tkinter.messagebox.showerror("Error", "An error occurred when creating the task.")
            self.window_handle.destroy() # Close the window and return
            return

        message_count = 0

        while not self.stop_scan:
            try: resp_obj = json.loads(provisioning.caladium_api(f"/api/tasks/{self.task_id}"))
            except: ...

            if len(resp_obj["updates"]) > message_count:
                [self._display_update(update) for update in resp_obj["updates"][message_count:]]
                message_count = len(resp_obj["updates"])

            # Allow UI to update
            self.main_window.update()
            self.main_window.after(100)

    def _stop_scan(self):
        if self.scan_in_progress:
            self.stop_scan = True
            provisioning.caladium_api(f"/api/tasks/{self.task_id}", method="DELETE")
            self.window_handle.destroy()

    def start(self, data, config):
        @tkthread.main(self.main_window)
        def start_thread(): self._scan_file(data, config)
