#
#  tasks.py
#  caladium
#
#  Created by Declan Kelly on 11-12-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, socket, threading, uuid

import flask

import database, workers

tasks = flask.Blueprint(__name__, "tasks")

def scan_file(task_id, scan_file_obj):
    tasks_database = database.get_database("tasks")
    tasks_database[task_id] = {"state": "Running"}

    workers_dict = workers.get_workers_route()
    if len(list(workers_dict)) == 0:
        tasks_database[task_id] = {"state": "Failure"}
        return

    worker_address = workers_dict[list(workers_dict)[0]]["workerAddress"]
    host, port = worker_address.strip().split(':')

    sandbox_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sandbox_socket.connect((host, int(port)))
    sandbox_socket.send(scan_file_obj)
    tasks_database[task_id] = json.loads(sandbox_socket.recv(1024).decode("utf-8"))
    sandbox_socket.close()

@tasks.get("/api/tasks")
def get_tasks_route():
    return database.get_database("tasks").add(as_list=True)

@tasks.get("/api/tasks/<task_id>")
def get_task_progress_route(task_id):
    return tasks_database[task_id]

@tasks.post("/api/tasks")
def create_task_route():
    task_id = str(uuid.uuid1())

    thread_obj = threading.Thread(args=(task_id, flask.request.get_data()), target=scan_file)
    thread_obj.start()

    return task_id

