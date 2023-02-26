# 02-26-2023 12:31

import tkinter.ttk

class PreferencesFrame(tkinter.ttk.Frame):
    def __init__(self):
        super().__init__()
        self.columnconfigure(0, weight=1)
        
        self.preference_items = [
            ["Uninstall Caladium", None],
            ["Change Scanning Directory", None]
        ]

        # Add the widget
        self.preference_items[0][1] = tkinter.ttk.Button(self, command=lambda: self._unistall_caladium())
        self.preference_items[0][1]["text"] = "Uninstall Caladium"

        self.preference_items[1][1] = self.preference_items[0][1]

        for i, item in enumerate(self.preference_items):
            label = tkinter.ttk.Label(self)
            label["text"] = item[0]
            label.grid(row=i, column=0, sticky="w")

            widget = tkinter.ttk.Button(self, command=item[1])
            widget["text"] = item[0]
            widget.grid(row=i, column=1, sticky="e")

    def _uninstall_caladium(self):
        print("Uninstall Caladium")
