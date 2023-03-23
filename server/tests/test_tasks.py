#
#  test_tasks.py
#  caladium
#
#  Created by Declan Kelly on 09-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import setup

class TasksTestCase(setup.EndPointTestCase):
    def setUp(self):
        example_record = {"state": "complete"}
        super().setUp("/api/tasks", example_record)

