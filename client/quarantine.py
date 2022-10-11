#
#  quarantine.py
#  caladium
#
#  Created by Declan Kelly on 11-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, os, secrets, uuid

class Quarantine:
    def __init__(self, quarantine_location):
        self.quarantine_location = quarantine_location
        self.xor_key_size = 16
        self.index_json_location = quarantine_location + os.path.sep + "index.json"

        for i in range(1, len(self.index_json_location.split(os.path.sep))):
            dir_path = os.path.sep.join(self.index_json_location.split(os.path.sep)[:i])
            if not os.path.isdir(dir_path): os.mkdir(dir_path)

        if os.path.exists(self.index_json_location):
            with open(self.index_json_location) as index_json_handle:
                self.index = json.load(index_json_handle)
        else:
            self.index = []

    def _save_index_to_disk(self):
        with open(self.index_json_location, "w") as index_json_handle:
            json.dump(self.index, index_json_handle)

    def _xor_bytes(self, data_bytes, xor_key_bytes):
        data_bytes = [i for i in data_bytes]

        for i in range(len(data_bytes)):
            data_bytes[i] ^= xor_key_bytes[i % len(xor_key_bytes)]

        return bytes(data_bytes)

    def get_file_list(self):
        return self.index

    def quarantine_file(self, file_location):
        file_id = str(uuid.uuid1())
        file_xor_key = secrets.token_bytes(self.xor_key_size)

        with open(file_location, "rb") as input_file_handle:
            file_data = file_xor_key + self._xor_bytes(input_file_handle.read(), file_xor_key)

            with open(self.quarantine_location + os.path.sep + file_id, "wb") as output_file_handle:
                output_file_handle.write(file_data)

        os.remove(file_location)

        self.index += [{
            "file_location": file_location,
            "file_id": file_id
        }]
        self._save_index_to_disk()

        return file_id

    def restore_file(self, file_id):
        with open(self.quarantine_location + os.path.sep + file_id, "rb") as input_file_handle:
            file_data = input_file_handle.read()
            file_xor_key, file_data = file_data[:self.xor_key_size], file_data[self.xor_key_size:]
            file_data = self._xor_bytes(file_data, file_xor_key)
            file_location = [*filter(lambda quarantine_record: quarantine_record["file_id"] == file_id, self.index)][0]["file_location"]

            with open(file_location, "wb") as output_file_handle:
                output_file_handle.write(file_data)

        os.remove(self.quarantine_location + os.path.sep + file_id)

        self.index = [*filter(lambda quarantine_record: quarantine_record["file_id"] != file_id, self.index)]
        self._save_index_to_disk()

