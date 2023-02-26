#
#  workers.py
#  caladium
#
#  Created by Declan Kelly on 04-12-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, socket, struct, uuid

import flask

import database

def read_json_from_socket(sandbox_socket):
    # Packets begin with a 4-byte unsigned integer indicating the size of the JSON data
    json_size = struct.unpack(">I", sandbox_socket.recv(4))[0]
    # Read the JSON data of that size
    json_data = sandbox_socket.recv(json_size).decode("utf-8")
    return json.loads(json_data)

def establish_connection(server_address):
    # Connect to that server_address
    host, port = server_address.strip().split(':')

    sandbox_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sandbox_socket.connect((host, int(port)))
    return sandbox_socket

class WorkerRecord(database.DatabaseRecord):
    database_name = "workers"

    def ping(self):
        sandbox_socket = establish_connection(self.get("workerAddress"))
        sandbox_socket.send(json.dumps({"command": "ping"}).encode())
        ping_resp_json = read_json_from_socket(sandbox_socket)
        sandbox_socket.close()

        ping_resp = flask.Response()
        ping_resp.headers["Content-Type"] = "application/json"
        ping_resp.set_data(json.dumps(ping_resp_json))
        return ping_resp

workers = flask.Blueprint(__name__, "workers")

@workers.get("/api/workers")
def get_records_route():
    return database.get_caladium_collection("workers")

@workers.post("/api/workers")
def create_workers_route():
    new_document = json.loads(flask.request.data.decode("utf-8"))
    return str(database.create(WorkerRecord, new_document))

@workers.delete("/api/workers")
def delete_all_workers_route():
    for worker_id in database.get_caladium_collection("workers"):
        database.get(WorkerRecord, worker_id).delete()
    return {}

@workers.delete("/api/workers/<worker_id>")
def delete_workers_route(worker_id):
    if worker := database.get(WorkerRecord, worker_id):
        worker.delete()
    return {}

@workers.get("/api/workers/ping/<worker_id>")
def ping_workers_route(worker_id):
    if worker := database.get(WorkerRecord, worker_id):
        return worker.ping()

