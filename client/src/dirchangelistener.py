#
#  dirchangelistener.py
#  caladium
#
#  Created by Declan Kelly on 17-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import os, sys

import provisioning

# Returns the path to the user's downloads directory
# Supports Windows and macOS
def get_downloads_dir():
    return (os.environ["USERPROFILE"] if sys.platform == "win32" else os.environ["HOME"]) + "{0}Downloads".format(os.path.sep)

class DirChangeListener:
    def __init__(self, callback_func, main_window, update_scan_dir_label_func):
        # Setup directory change listener
        self.config = provisioning.get_config()
        self.callback_func = callback_func
        self.main_window = main_window
        self.update_scan_dir_label_func = update_scan_dir_label_func

    def _get_scanning_dir(self):
        return provisioning.get_config().get("scanning_directory", get_downloads_dir())

    def start(self):
        # Get the initial state of the directory
        scan_directory = self._get_scanning_dir()
        current_dir_state = os.listdir(scan_directory)

        # Continuously check the downloads directory for changes
        while True:
            self.update_scan_dir_label_func(current_scan_directory := self._get_scanning_dir())
            latest_dir_state = os.listdir(current_scan_directory)

            # Check if the scanning directory has changed
            if current_scan_directory != scan_directory:
                scan_directory = current_scan_directory
                current_dir_state = latest_dir_state
                continue

            # Check for new files
            for file_item in latest_dir_state:
                if file_item not in current_dir_state:
                    self.callback_func(scan_directory + os.path.sep + file_item)

            current_dir_state = latest_dir_state

            self.main_window.update()
            self.main_window.after(100)
