#
#  __main__.py
#  caladium
#
#  Created by Declan Kelly on 10-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import hashlib, json, sys, time

import flask, requests, uuid

import clients, patterns, tasks, workers

preferences = {
    "administrator_password": None,
    "authorisation_tokens": [],
    "auto_provision": False,
}

app = flask.Flask(__name__)
app.register_blueprint(clients.clients)
app.register_blueprint(patterns.patterns)
app.register_blueprint(tasks.tasks)
app.register_blueprint(workers.workers)

@app.route("/")
@app.route("/<path:index_path>")
def root_page(index_path=None):
    with open("static/index.html") as index_html_handle:
        return index_html_handle.read()

@app.route("/css/<path:css_file_path>")
def serve_css_file(css_file_path):
    milligram_dist_location = "https://raw.githubusercontent.com/milligram/milligram/master/dist/"
    css_file_dict = {
        "milligram.min.css": {"content_type": "text/css"},
        "milligram.min.css.map": {"content_type": "application/json"}
    }

    if css_file_path in css_file_dict:
        milligram_dist_resp = requests.get(milligram_dist_location + css_file_path).text
        return flask.Response(milligram_dist_resp, headers={"Content-Type": css_file_dict[css_file_path]["content_type"]})
    else:
        return str()

@app.route("/js/<path:js_file_path>")
def serve_js_file(js_file_path):
    return flask.send_from_directory("static/js/", js_file_path)

@app.post("/api/auto_provision")
def auto_provision_route():
    if preferences["auto_provision"]:
        return clients.create_clients_route()
    else:
        resp_obj = flask.Response()
        resp_obj.status_code = 403
        resp_obj.set_data("Automatic provisioning is disabled")
        return resp_obj

@app.post("/api/login")
def login_route():
    req_body_obj = json.loads(flask.request.get_data())
    username, password = req_body_obj["username"], req_body_obj["password"]

    if username == "root" and preferences["administrator_password"] == hashlib.sha256(password.encode()).hexdigest():
        token = str(uuid.uuid1())
        preferences["authorisation_tokens"] += [token]
        return {"valid": True, "Authorisation": token}
    else:
        return {"valid": False, "message": "Incorrect username or password"}

def update_password(new_password):
    preferences["administrator_password"] = hashlib.sha256(new_password.encode()).hexdigest()

@app.get("/api/admin/preferences")
def preferences_route():
    return preferences

@app.put("/api/admin/preferences")
def update_password_route():
    put_payload = json.loads(flask.request.get_data())

    if "password" in put_payload:
        if new_password := json.loads(flask.request.get_data()).get("password", None):
            update_password(new_password)
    else:
        for preference_field in put_payload:
            preferences[preference_field] = put_payload[preference_field]

    return {}

@app.get("/api/admin/statistics")
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

def before_request():
    path, resp_obj, token = flask.request.path, flask.Response(), flask.request.headers.get("Authorisation", None)

    if path == "/api/auto_provision":
        ...
    elif path.startswith("/api/tasks"):
        if token not in preferences["authorisation_tokens"] and token not in clients.get_authorisation_tokens():
            resp_obj.status_code = 403
            resp_obj.set_data("Invalid authorisation token")
            return resp_obj
    elif path.startswith("/api") and not path.startswith("/api/login"):
        if token not in preferences["authorisation_tokens"]:
            resp_obj.status_code = 403
            resp_obj.set_data("Invalid authorisation token")
            return resp_obj

def after_request(response_obj):
    response_obj.headers.add("Access-Control-Allow-Headers", '*')
    response_obj.headers.add("Access-Control-Allow-Methods", '*')
    response_obj.headers.add("Access-Control-Allow-Origin", '*')
    return response_obj

def main(argv):
    port_number = int(argv[1]) if len(argv) > 1 else 8080
    update_password("root")

    app.before_request(before_request)
    app.after_request(after_request)
    app.run(host="0.0.0.0", port=port_number)

if __name__ == "__main__":
    main(sys.argv)

