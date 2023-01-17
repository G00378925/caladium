#
#  tasks.py
#  caladium
#
#  Created by Declan Kelly on 11-12-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, socket, struct, threading, uuid

import flask

import database, workers

class TaskRecord(database.DatabaseRecord):
    database_name = "tasks"

tasks = flask.Blueprint(__name__, "tasks")

def read_json_from_socket(sandbox_socket):
    json_size = struct.unpack(">I", sandbox_socket.recv(4))[0]
    json_data = sandbox_socket.recv(json_size).decode("utf-8")
    return json.loads(json_data)

def scan_file(scan_file_obj):
    task = database.create(TaskRecord, {"state": "Running", "updates": []})

    def scan_file_thread():
        workers_dict = workers.get_workers_route()
        if len(list(workers_dict)) == 0:
            task.set("state", {"state": "Failure"})
            return

        worker_address = workers_dict[list(workers_dict)[0]]["workerAddress"]
        host, port = worker_address.strip().split(':')

        sandbox_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sandbox_socket.connect((host, int(port)))
        sandbox_socket.send(scan_file_obj)

        while True:
            updates_list = task.get("updates").copy()
            updates_list += [read_json_from_socket(sandbox_socket)]
            task.set("updates", updates_list)

            task.set("state", updates_list[-1]["state"])
            if updates_list[-1]["state"] == "complete": break

        sandbox_socket.close()

    thread_obj = threading.Thread(target=scan_file_thread)
    thread_obj.start()

    return str(task)

@tasks.get("/api/tasks")
def get_tasks_route():
    return database.get_caladium_collection("tasks")

@tasks.get("/api/tasks/<task_id>")
def get_task_progress_route(task_id):
    if task := database.get(TaskRecord, task_id):
        return str(task)
    return str()

@tasks.delete("/api/tasks")
def delete_all_task_route():
    for task in database.get_caladium_collection("task"):
        database.get_database("tasks").get(task).delete()
    return str()

@tasks.delete("/api/tasks/<task_id>")
def delete_tasks_route(task_id):
    if task := database.get(TaskRecord, task_id):
        task.delete()
    return {}

@tasks.post("/api/tasks")
def create_task_route():
    return scan_file(flask.request.get_data())

