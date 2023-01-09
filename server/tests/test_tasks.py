#
#  test_tasks.py
#  caladium
#
#  Created by Declan Kelly on 09-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import unittest

import requests

from setup import *

class TasksTestCase(unittest.TestCase):
    def setupClass(self):
        self.http_headers = get_http_headers(CALADIUM_SERVER_ADDRESS, "root", "root")

