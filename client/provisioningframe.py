#
#  provisioningframe.py
#  caladium
#
#  Created by Declan Kelly on 05-02-2023.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import tkinter, tkinter.filedialog, tkinter.ttk

import provisioning

class ProvisioningFrame(tkinter.ttk.Frame):
    def __init__(self, main_window, provisioning_complete):
        super().__init__(main_window)
        self.quarantine_obj = quarantine_obj
        self.quarantine_index_dict = {}

        self.quarantine_list = tkinter.Listbox(self)
        self._update_quarantine_list()
        self.quarantine_list.pack(fill=tkinter.BOTH)

        self.quarantine_button = tkinter.Button(self, command=lambda: self._quarantine_file())
        self.quarantine_button["text"] = "Quarantine file"
        self.quarantine_button.pack()

    def _quarantine_file(self):
        file_handle = tkinter.filedialog.askopenfile("rb")
        if not file_handle: return
        file_location = file_handle.name
        file_handle.close()

        self.quarantine_obj.quarantine_file(file_location)
        self._update_quarantine_list()

    def _update_quarantine_list(self):
        self.quarantine_list.delete(0, len(list(self.quarantine_index_dict)))
        self.quarantine_index_dict = {}

        index = 0
        for file_record in self.quarantine_obj.get_file_list():
            self.quarantine_index_dict[index] = file_record
            self.quarantine_list.insert(index, file_record["file_location"])
            index += 1

