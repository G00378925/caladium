#
#  test_patterns.py
#  caladium
#
#  Created by Declan Kelly on 17-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import setup

class PatternsTestCase(setup.EndPointTestCase):
    def setUp(self):
        example_record = {"pattern_string": ""}
        super().setUp("/api/patterns", example_record)

