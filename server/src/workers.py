#
#  workers.py
#  caladium
#
#  Created by Declan Kelly on 04-12-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, uuid

import flask

workers = flask.Blueprint(__name__, "workers")

workers_database = {}

@workers.get("/api/workers")
def get_workers_route():
    global workers_database
    return workers_database

@workers.post("/api/workers")
def create_workers_route():
    global workers_database
    new_worker_id = str(uuid.uuid1())
    workers_database[new_worker_id] = json.loads(flask.request.data.decode("utf-8"))
    return {"workerID": new_worker_id}

@workers.delete("/api/workers/<worker_id>")
def delete_workers_route(worker_id):
    global workers_database
    del workers_database[worker_id]
    return {}

