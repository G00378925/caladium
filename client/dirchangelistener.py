#
#  dirchangelistener.py
#  caladium
#
#  Created by Declan Kelly on 17-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import os, threading, time

class DirChangeListener:
    def __init__(self, path_list, callback_func):
        self.path_list = path_list
        self.callback_func = callback_func

    def start(self):
        def _change_check_loop():
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

                time.sleep(1)

        self.thread_obj = threading.Thread(target=_change_check_loop)
        self.thread_obj.start()

