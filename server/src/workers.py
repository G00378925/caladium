#
#  workers.py
#  caladium
#
#  Created by Declan Kelly on 04-12-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, socket, struct

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

    def _send_command(self, command):
        sandbox_socket = establish_connection(self.get("workerAddress"))
        sandbox_socket.send(json.dumps({"command": command}).encode())
        command_resp_json = read_json_from_socket(sandbox_socket)
        sandbox_socket.close()
        return command_resp_json
    
    def _send_response(self, response):
        resp = flask.Response()
        resp.headers["Content-Type"] = "application/json"
        resp.set_data(json.dumps(response))
        return resp

    def ping(self):
        return self._send_response(self._send_command("ping"))
    
    def kill(self):
        try: self._send_command("kill")
        except: ... # For once an exception is a good thing

workers = flask.Blueprint(__name__, "workers")

# Get all workers
@workers.get("/api/workers")
def get_records_route():
    return database.get_caladium_collection("workers")

# Create a new worker
@workers.post("/api/workers")
def create_workers_route():
    new_document = json.loads(flask.request.data.decode("utf-8"))
    return str(database.create(WorkerRecord, new_document))

# Delete all workers
@workers.delete("/api/workers")
def delete_all_workers_route():
    for worker_id in database.get_caladium_collection("workers"):
        database.get(WorkerRecord, worker_id).delete()
    return {}

# Delete a specific worker
@workers.delete("/api/workers/<worker_id>")
def delete_workers_route(worker_id):
    if worker := database.get(WorkerRecord, worker_id):
        worker.delete()
    return {}

# Ping a worker
@workers.get("/api/workers/ping/<worker_id>")
def ping_workers_route(worker_id):
    if worker := database.get(WorkerRecord, worker_id):
        return worker.ping()

# Kill a worker
@workers.post("/api/workers/kill/<worker_id>")
def kill_workers_route(worker_id):
    if worker := database.get(WorkerRecord, worker_id):
        worker.kill()
        return {}
