#
#  clients.py
#  caladium
#
#  Created by Declan Kelly on 20-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import base64, json

import flask

import database

# List of client authorisation tokens
authorisation_tokens = []

class ClientRecord(database.DatabaseRecord):
    database_name = "clients"

clients = flask.Blueprint(__name__, "clients")

def get_authorisation_tokens():
    global authorisation_tokens
    return authorisation_tokens

def update_authorisation_tokens():
    global authorisation_tokens
    authorisation_tokens = [database.get(ClientRecord, client_id).get("_id")
                            for client_id in database.get_caladium_collection("clients")]

update_authorisation_tokens()

@clients.get("/api/clients")
def get_records_route():
    clients = database.get_caladium_collection("clients")
    for client_id in clients:
        token_obj = {
            "authorisation_token": client_id,
            "server_address": flask.request.headers["Host"]
        }
        # Generate JSON provisioning profile
        clients[client_id]["token"] = base64.b64encode(json.dumps(token_obj).encode()).decode("utf-8")
    return clients

@clients.post("/api/clients")
def create_clients_route():
    resp_str = str(database.create(ClientRecord, {}))
    update_authorisation_tokens()
    return resp_str

@clients.delete("/api/clients")
def delete_all_clients_route():
    for client_id in database.get_caladium_collection("clients"):
        database.get(ClientRecord, client_id).delete()
    return {}

@clients.delete("/api/clients/<client_id>")
def delete_client_route(client_id):
    if client := database.get(ClientRecord, client_id):
        authorisation_tokens.remove(client_id) # Remove the client's auth token
        client.delete()
    return {}

