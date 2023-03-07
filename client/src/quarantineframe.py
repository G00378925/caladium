#
#  quarantineframe.py
#  caladium
#
#  Created by Declan Kelly on 12-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import tkinter

class QuarantineFrame(tkinter.ttk.Frame):
    def __init__(self, main_window, quarantine_obj):
        super().__init__(main_window)
        self.quarantine_obj = quarantine_obj
        self.quarantine_index_dict = {}
        self.columnconfigure(0, weight=1)
        
        self.quarantine_list = tkinter.Listbox(self)
        self._update_quarantine_list()
        self.quarantine_list.grid(column=0, row=0, sticky="nsew", rowspan=1, columnspan=2)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Add bottom buttons for quarantining and restoring files
        self.quarantine_button = tkinter.Button(self, command=lambda: self._quarantine_file())
        self.quarantine_button["text"] = "Quarantine file"
        self.quarantine_button["width"] = 30
        self.quarantine_button.grid(column=0, row=1, columnspan=1, sticky="w", padx=50)
        
        self.restore_button = tkinter.Button(self, command=lambda: self._restore_file())
        self.restore_button["text"] = "Restore file"
        self.restore_button["width"] = 30
        self.restore_button.grid(column=1, row=1, columnspan=1, sticky="e", padx=50)

    # Executed upon the quarantine button being pressed
    def _quarantine_file(self):
        file_handle = tkinter.filedialog.askopenfile("rb")
        if not file_handle: return
        file_location = file_handle.name
        file_handle.close()

        self.quarantine_obj.quarantine_file(file_location)
        self._update_quarantine_list()

    # Executed upon the restore button being pressed
    def _restore_file(self):
        if len(selected_items := self.quarantine_list.curselection()) == 1:
            try:
                self.quarantine_obj.restore_file(self.quarantine_index_dict[selected_items[0]]["file_id"])
            except FileNotFoundError:
                tkinter.messagebox.showerror("Error", "Directory that file was quarantined from no longer exists.")
            finally:
                self._update_quarantine_list()

    # Updates the quarantine list in the quarantine frame
    def _update_quarantine_list(self):
        self.quarantine_list.delete(0, len(list(self.quarantine_index_dict)))
        self.quarantine_index_dict = {}

        index = 0
        for file_record in self.quarantine_obj.get_file_list():
            self.quarantine_index_dict[index] = file_record
            self.quarantine_list.insert(index, file_record["file_location"])
            index += 1

