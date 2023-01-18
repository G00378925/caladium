#
#  test_tasks.py
#  caladium
#
#  Created by Declan Kelly on 09-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import unittest

import requests

import setup

class TasksTestCase(setup.EndPointTestCase):
    def setUp(self):
        example_record = {}
        super().setUp("/api/tasks", example_record)

