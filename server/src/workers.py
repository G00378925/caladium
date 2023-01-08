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

class WorkerRecord(database.DatabaseRecord):
    database_name = "workers"

    def ping(self):
        worker_address = self.get("workerAddress")
        return {"_id": self.get("_id")}

workers = flask.Blueprint(__name__, "workers")

@workers.get("/api/workers")
def get_workers_route():
    return database.get_caladium_collection("workers")

@workers.post("/api/workers")
def create_workers_route():
    new_document = json.loads(flask.request.data.decode("utf-8"))
    return str(database.create(WorkerRecord, new_document))

@workers.delete("/api/workers/<worker_id>")
def delete_workers_route(worker_id):
    if worker := database.get(WorkerRecord, worker_id):
        worker.delete()
    return {}

@workers.get("/api/workers/ping/<worker_id>")
def ping_workers_route(worker_id):
    if worker := database.get(WorkerRecord, worker_id):
        return worker.ping()

