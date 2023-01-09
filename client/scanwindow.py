#
#  scanwindow.py
#  caladium
#
#  Created by Declan Kelly on 09-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import tkinter, tkinter.scrolledtext, tkinter.ttk

class ScanWindow:
    def __init__(self):
        self.window_handle = tkinter.Tk()

        self.scrolled_text = tkinter.scrolledtext.ScrolledText(self.window_handle)
        self.scrolled_text.grid(row=0, column=0, columnspan=2)
        for i in range(100): self.scrolled_text.insert(tkinter.CURRENT, "Caladium\n")

        self.progress_bar = tkinter.ttk.Progressbar(self.window_handle)
        self.progress_bar.grid(row=1, column=0, columnspan=2)

        self.window_handle.mainloop()

ScanWindow().mainloop()

