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
    return f"{os.path.expanduser('~')}{os.path.sep}Downloads"

class DirChangeListener:
    def __init__(self, callback_func, main_window, update_scan_dir_label_func):
        # Setup directory change listener
        self.config = provisioning.get_config()
        self.callback_func = callback_func
        self.main_window = main_window
        self.update_scan_dir_label_func = update_scan_dir_label_func

        self.update_scan_dir_label_func(self._get_scanning_dir())

    # Fetch the scanning directory from the config
    def _get_scanning_dir(self):
        return provisioning.get_config().get("scanning_directory", get_downloads_dir())
    
    # Fetch the files in the directory being scanned
    def _get_dir_state(self, dir_path):
        try:
            return os.listdir(dir_path)
        except:
            # If there is a problem reading the directory, unprovision Caladium
            provisioning.unprovision_caladium()
            sys.exit(0)

    def start(self):
        # Get the initial state of the directory
        scan_directory = self._get_scanning_dir()
        current_dir_state = self._get_dir_state(scan_directory)

        # Continuously check the downloads directory for changes
        while True:
            current_scan_directory = self._get_scanning_dir()
            latest_dir_state = self._get_dir_state(current_scan_directory)

            # Check if the scanning directory has changed
            if current_scan_directory != scan_directory:
                # Update the main frame label
                self.update_scan_dir_label_func(current_scan_directory)

                scan_directory = current_scan_directory
                current_dir_state = latest_dir_state
                continue

            # Check for new files
            for file_item in latest_dir_state:
                if file_item not in current_dir_state:
                    # Prompt user the scan new file
                    self.callback_func(scan_directory + os.path.sep + file_item)

            # Set the new state of the directory
            current_dir_state = latest_dir_state

            # Give tkinter some time to update the UI
            self.main_window.update()
            self.main_window.after(100)
