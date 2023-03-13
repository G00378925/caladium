#
#  tasks.py
#  caladium
#
#  Created by Declan Kelly on 11-12-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, random, threading, uuid

import flask

import database, patterns, workers

class TaskRecord(database.DatabaseRecord):
    database_name = "tasks"

tasks = flask.Blueprint(__name__, "tasks")

def scan_file(scan_file_obj):
    task = database.create(TaskRecord, {"state": "Running", "updates": []})
    scan_file_obj = json.loads(scan_file_obj)

    # Check if there is any available workers
    if len(free_workers := workers.get_free_workers()) == 0:
        updates_list = task.get("updates").copy()
        updates_list += [{"type": "message", "text": "No workers available currently"}]
        task.set("state", "complete")

        # Send a 404 back to the client, indicating this
        return flask.Response("No free workers to take job", status=404) # Return 404 back to client

    # Try and initialise a job
    try:
        random_worker = random.choice(free_workers)

        task.set("worker_id", random_worker["_id"])
        worker = database.get(workers.WorkerRecord, random_worker["_id"])

        sandbox_socket = workers.establish_connection(random_worker["workerAddress"])
        scan_file_obj["patterns"] = patterns.get_patterns()
        sandbox_socket.send(json.dumps(scan_file_obj).encode())

        # Try and recieve initial response
        # Anything over 2 seconds is a failure
        sandbox_socket.settimeout(2)
        updates_list = task.get("updates").copy()
        updates_list += [workers.read_json_from_socket(sandbox_socket)]
        sandbox_socket.settimeout(None)
    except:
        task.set("state", "failed")
        worker.set("busy", False)
        sandbox_socket.close()
        return flask.Response("", status=404) # Return 404 back to client

    def scan_file_thread(): # Continously recieve updates from the worker
        try:
            worker.set("busy", True)

            while True:
                updates_list = task.get("updates").copy()
                updates_list += [workers.read_json_from_socket(sandbox_socket)]
                task.set("updates", updates_list)

                if updates_list[-1]["type"] == "state":
                    task.set("state", updates_list[-1]["state"])
                    if updates_list[-1]["state"] == "complete": break
        except: ...
        finally:
            # Cleanup
            worker.set("busy", False)
            sandbox_socket.close()

    threading.Thread(target=scan_file_thread).start()
    return str(task)

@tasks.get("/api/tasks")
def get_records_route():
    return database.get_caladium_collection("tasks")

@tasks.get("/api/tasks/test_connection")
def test_connection_route():
    return "OK"

@tasks.get("/api/tasks/<task_id>")
def get_task_progress_route(task_id):
    if task := database.get(TaskRecord, task_id):
        return str(task)
    return {}

@tasks.delete("/api/tasks")
def delete_all_tasks_route():
    for task_id in database.get_caladium_collection("tasks"):
        database.get(TaskRecord, task_id).delete()
    return {}

@tasks.delete("/api/tasks/<task_id>")
def delete_tasks_route(task_id):
    if task := database.get(TaskRecord, task_id):
        task.delete()
    return {}

@tasks.post("/api/tasks")
def create_task_route():
    return scan_file(flask.request.get_data())

@tasks.delete("/api/tasks/kill/<task_id>")
def kill_task_route(task_id):
    if task := database.get(TaskRecord, task_id):
        if worker := database.get(workers.WorkerRecord, task.get("worker_id")):
            worker.kill()
    return {}