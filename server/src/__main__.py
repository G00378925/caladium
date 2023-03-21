#
#  __main__.py
#  caladium
#
#  Created by Declan Kelly on 10-10-2022.
#  Copyright © 2022 Declan Kelly. All rights reserved.
#

import hashlib, json, sys

import flask, requests, uuid

import clients, patterns, preferences, tasks, workers

# Setup flask app and other collections of API endpoints
app = flask.Flask(__name__)
app.register_blueprint(clients.clients)
app.register_blueprint(patterns.patterns)
app.register_blueprint(preferences.preferences)
app.register_blueprint(tasks.tasks)
app.register_blueprint(workers.workers)

# Serve the index.html
@app.route("/")
@app.route("/<path:index_path>")
def root_page(index_path=None):
    with open("static/index.html") as index_html_handle:
        return index_html_handle.read()

# Serve CSS files
@app.route("/css/<path:css_file_path>")
def serve_css_file(css_file_path):
    milligram_dist_location = "https://raw.githubusercontent.com/milligram/milligram/master/dist/"
    css_file_dict = {
        "milligram.min.css": {"content_type": "text/css"},
        "milligram.min.css.map": {"content_type": "application/json"}
    }

    # Find the path in the dictionary above
    if css_file_path in css_file_dict:
        # Fetch the file from the milligram repository
        milligram_dist_resp = requests.get(milligram_dist_location + css_file_path).text
        return flask.Response(milligram_dist_resp, headers={"Content-Type": css_file_dict[css_file_path]["content_type"]})
    else:
        return str()

# Serve JavaScript files
@app.route("/js/<path:js_file_path>")
def serve_js_file(js_file_path):
    return flask.send_from_directory("static/js/", js_file_path)

@app.post("/api/auto_provision")
def auto_provision_route():
    if globals()["preferences"]["auto_provision"]:
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

    if username == "root" and preferences.preferences_dict["administrator_password"] == hashlib.sha256(password.encode()).hexdigest():
        token = str(uuid.uuid1())
        preferences.preferences_dict["authorisation_tokens"] += [token]
        return {"valid": True, "Authorisation": token}
    else:
        return {"valid": False, "message": "Incorrect username or password"}

# Execute before every request, used to check if the user is authorised to access the requested endpoint
def before_request():
    path, resp_obj, token = flask.request.path, flask.Response(), flask.request.headers.get("Authorisation", None)

    # Allows auto provisioning
    if path == "/api/auto_provision" and preferences.preferences_dict["auto_provision"]:
        ...
    # Windows clients authentication
    elif path.startswith("/api/tasks") or path.startswith("/api/workers"):
        if token not in preferences.preferences_dict["authorisation_tokens"] and token not in clients.get_authorisation_tokens():
            resp_obj.status_code = 403
            resp_obj.set_data("Invalid authorisation token")
            return resp_obj
    # Dashboard authentication
    elif path.startswith("/api") and not path.startswith("/api/login"):
        if token not in preferences.preferences_dict["authorisation_tokens"]:
            resp_obj.status_code = 403
            resp_obj.set_data("Invalid authorisation token")
            return resp_obj

# Used to apply CORS headers to every response
def after_request(response_obj):
    response_obj.headers.add("Access-Control-Allow-Headers", '*')
    response_obj.headers.add("Access-Control-Allow-Methods", '*')
    response_obj.headers.add("Access-Control-Allow-Origin", '*')
    return response_obj

def main(argv):
    # If a port number is specified, use it, otherwise use 8080
    port_number = int(argv[1]) if len(argv) > 1 else 8080

    # Add request/response handlers
    app.before_request(before_request)
    app.after_request(after_request)
    app.run(host="0.0.0.0", port=port_number, threaded=False, processes=1)

if __name__ == "__main__":
    main(sys.argv)
