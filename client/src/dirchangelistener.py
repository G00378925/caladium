#
#  dirchangelistener.py
#  caladium
#
#  Created by Declan Kelly on 17-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import os, sys

# Returns the path to the user's downloads directory
# Supports Windows and macOS
def get_downloads_dir():
    return (os.environ["USERPROFILE"] if sys.platform == "win32" else os.environ["HOME"]) + "{0}Downloads".format(os.path.sep)

class DirChangeListener:
    def __init__(self, config, callback_func, main_window):
        # Setup directory change listener
        self.config = config
        self.callback_func = callback_func
        self.main_window = main_window

    def start(self):
        # Get the initial state of the directory
        scan_directory = self.config.get("scanning_directory", get_downloads_dir())
        current_dir_state = os.listdir(scan_directory)

        # Continuously check the downloads directory for changes
        while True:
            latest_dir_state = os.listdir(scan_directory)

            # Check for new files
            for file_item in latest_dir_state:
                if file_item not in current_dir_state:
                    self.callback_func(scan_directory + os.path.sep + file_item)

            current_dir_state = latest_dir_state

            self.main_window.update()
            self.main_window.after(100)
