#
#  patterns.py
#  caladium
#
#  Created by Declan Kelly on 15-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import json

import flask

import database

class PatternRecord(database.DatabaseRecord):
    database_name = "patterns"

patterns = flask.Blueprint(__name__, "patterns")

@patterns.get("/api/patterns")
def get_patterns_route():
    return database.get_caladium_collection("patterns")

@patterns.post("/api/patterns")
def create_patterns_route():
    new_document = json.loads(flask.request.data.decode("utf-8"))
    return str(database.create(PatternRecord, new_document))

@patterns.delete("/api/patterns/<pattern_id>")
def delete_pattern_route(pattern_id):
    if pattern := database.get(PatternRecord, pattern_id):
        pattern.delete()
    return {}

