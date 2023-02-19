#
#  dirchangelistener.py
#  caladium
#
#  Created by Declan Kelly on 17-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import os

class DirChangeListener:
    def __init__(self, path_list, callback_func, main_window):
        self.path_list = path_list
        self.callback_func = callback_func
        self.main_window = main_window

    def start(self):
        current_dir_state = {}
        for path in self.path_list:
            current_dir_state[path] = os.listdir(path)

        while True:
            for path in self.path_list:
                latest_dir_state = os.listdir(path)

                for file_item in latest_dir_state:
                    if file_item not in current_dir_state[path]:
                        self.callback_func(path + os.path.sep + file_item)

                current_dir_state[path] = latest_dir_state

            self.main_window.update()
            self.main_window.after(10000)
