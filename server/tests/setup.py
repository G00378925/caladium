#
#  setup.py
#  caladium
#
#  Created by Declan Kelly on 09-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import json, os, sys, unittest

import requests

if not os.environ.get("CALADIUM_SERVER_ADDRESS", None):
    sys.stderr.write("CALADIUM_SERVER_ADDRESS environmental variable must be set.")
    sys.exit(0)

CALADIUM_SERVER_ADDRESS = os.environ["CALADIUM_SERVER_ADDRESS"]

class EndPointTestCase(unittest.TestCase):
    def get_http_headers(self, username, password):
        data = json.dumps({"username": username, "password": password})
        token = json.loads(requests.post(f"http://{CALADIUM_SERVER_ADDRESS}/api/login", data=data).text)["Authorisation"]
        return {"Authorisation": token}

    def get_all_records(self):
        return json.loads(requests.get(f"http://{CALADIUM_SERVER_ADDRESS}{self.endpoint}", headers=self.http_headers).text)

    def create_new_record(self, new_record):
        requests.post(f"http://{CALADIUM_SERVER_ADDRESS}{self.endpoint}", data=json.dumps(new_record), headers=self.http_headers)

    def setUp(self, endpoint, example_record):
        self.endpoint = endpoint
        self.example_record = example_record
        self.http_headers = self.get_http_headers("root", "root")

        self.test_delete_all_records()

        if endpoint != "/api/tasks":
            for _ in range(5): self.create_new_record(self.example_record)

    def test_delete_all_records(self):
        requests.delete(f"http://{CALADIUM_SERVER_ADDRESS}{self.endpoint}", headers=self.http_headers)
        self.assertEqual(len(self.get_all_records()), 0)

    def test_create_5_records(self):
        record_count = len(self.get_all_records())

        for _ in range(5):
            self.create_new_record(self.example_record)

        self.assertEqual(len(self.get_all_records()), record_count + 5)
