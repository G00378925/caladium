#
#  test_workers.py
#  caladium
#
#  Created by Declan Kelly on 17-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import setup

class WorkersTestCase(setup.EndPointTestCase):
    def setUp(self):
        example_record = {"worker_address": "127.0.0.1"}
        super().setUp("/api/workers", example_record)

