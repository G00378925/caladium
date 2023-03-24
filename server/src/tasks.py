#
#  tasks.py
#  caladium
#
#  Created by Declan Kelly on 11-12-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import json, random, threading

import flask

import database, patterns, preferences, workers

class TaskRecord(database.DatabaseRecord):
    database_name = "tasks"

tasks = flask.Blueprint(__name__, "tasks")

def scan_file(scan_file_obj):
    task = database.create(TaskRecord, {"state": "executing", "updates": []})

    def append_update(update_obj):
        updates_list = task.get("updates").copy()

        # If update_obj is a string, convert it to a message update
        if type(update_obj) == str:
            update_obj = {"type": "message", "text": update_obj}

        updates_list += [update_obj] # Append to update to task updates list
        task.set("updates", updates_list)
    
    def scan_file_thread(scan_file_obj):
        # Check if there is any available workers
        if len(list_of_workers := workers.get_records_route()) > 0:
            try:
                random_worker = random.choice([*list_of_workers.values()])
                sandbox_socket = workers.establish_connection(random_worker["worker_address"])

                scan_file_obj = json.loads(scan_file_obj)
                scan_file_obj["patterns"] = patterns.get_patterns()
                scan_file_obj["dynamic-analysis"] = preferences.preferences_dict["dynamic_analysis"]
                sandbox_socket.send(json.dumps(scan_file_obj).encode())

                append_update(workers.read_json_from_socket(sandbox_socket))
            except:
                append_update("[-] Failed to connect to worker")
                task.set("state", "failed")
        else:
            append_update("[-] No workers available currently")
            task.set("state", "failed")

        if task.get("state") != "executing": return

        try: # Continously recieve updates from the worker
            while task.get("state") == "executing":
                append_update(workers.read_json_from_socket(sandbox_socket))

                if (updates_list := task.get("updates").copy())[-1]["type"] == "state":
                    task.set("state", updates_list[-1]["state"])
                    if updates_list[-1]["state"] == "clean": break
        except: ...
        finally:
            sandbox_socket.close()

    threading.Thread(target=scan_file_thread, args=(scan_file_obj,)).start()
    return str(task) # Return early

@tasks.get("/api/tasks")
def get_records_route():
    return database.get_caladium_collection("tasks")

@tasks.get("/api/tasks/test_connection")
def test_connection_route():
    return "OK"

# Fetch state of task
@tasks.get("/api/tasks/<task_id>")
def get_task_progress_route(task_id):
    if task := database.get(TaskRecord, task_id):
        return str(task)
    return {}

# Delete all tasks
@tasks.delete("/api/tasks")
def delete_all_tasks_route():
    for task_id in database.get_caladium_collection("tasks"):
        database.get(TaskRecord, task_id).delete()
    return {}

# Delete a specific task
@tasks.delete("/api/tasks/<task_id>")
def delete_tasks_route(task_id):
    if task := database.get(TaskRecord, task_id):
        task.delete()
    return {}

# Create a new task
@tasks.post("/api/tasks")
def create_task_route():
    return scan_file(flask.request.get_data())

# Kill a task
@tasks.delete("/api/tasks/kill/<task_id>")
def kill_task_route(task_id):
    if task := database.get(TaskRecord, task_id):
        if worker := database.get(workers.WorkerRecord, task.get("worker_id")):
            worker.kill()
    return {}