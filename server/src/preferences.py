# 20:29 20-03-2023

import json, hashlib, time

import flask

import clients, patterns, workers

preferences = flask.Blueprint("preferences", __name__)

# Used to store server preferences
preferences_dict = {
    "administrator_password": None, # Hash of the administrator password
    "authorisation_tokens": [], # List of tokens that can be used to access the dashboard
    "auto_provision": False, # If true, the server will automatically provision new clients
    "dynamic_analysis": True # If true, uploaded files will be analysed dynamically
}

def update_password(new_password):
    preferences_dict["administrator_password"] = hashlib.sha256(new_password.encode()).hexdigest()

update_password("root") # Set initial administrator password to "root"

@preferences.get("/api/preferences")
def preferences_route():
    return preferences_dict

@preferences.put("/api/preferences")
def update_password_route():
    put_payload = json.loads(flask.request.get_data())

    if "password" in put_payload:
        if new_password := json.loads(flask.request.get_data()).get("password", None):
            update_password(new_password)
    else:
        for preference_field in put_payload:
            preferences_dict[preference_field] = put_payload[preference_field]

    return {}

@preferences.get("/api/preferences/statistics")
def statistics_route():
    statistics = []

    for endpoint, label in zip([clients, patterns, workers], ["clients", "patterns", "workers"]):
        endpoint_statistics = {"plot_name": label + "-canvas", "plot_type": "barchart", "data": []}
        endpoints_records = endpoint.get_records_route()

        for record in endpoints_records.values():
            data, month = endpoint_statistics["data"], time.strftime("%b", time.localtime(record["creation_time"]))

            if month not in [subdata["title"] for subdata in data]:
                data += [{"colour": "green", "title": month, "value": 1}]
            else:
                [*filter(lambda subdata: subdata["title"] == month, data)][0]["value"] += 1

        statistics += [endpoint_statistics]

    return statistics
