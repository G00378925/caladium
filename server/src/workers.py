#
#  workers.py
#  caladium
#
#  Created by Declan Kelly on 04-12-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, uuid

import flask

import database

workers = flask.Blueprint(__name__, "workers")

class WorkerRecord(database.DatabaseRecord):
    database_name = "workers"

@workers.get("/api/workers")
def get_workers_route():
    return database.get_caladium_collection("workers")

@workers.post("/api/workers")
def create_workers_route():
    new_document = json.loads(flask.request.data.decode("utf-8"))
    return database.get_database("workers").save(new_document)

@workers.delete("/api/workers/<worker_id>")
def delete_workers_route(worker_id):
    if worker := database.get(WorkerRecord, worker_id):
        del worker
    return {}

