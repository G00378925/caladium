#
#  test_clients.py
#  caladium
#
#  Created by Declan Kelly on 20-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import unittest

import requests

import setup

class ClientsTestCase(setup.EndPointTestCase):
    def setUp(self):
        example_record = {"token": "token"}
        super().setUp("/api/clients", example_record)

