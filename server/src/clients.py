#
#  clients.py
#  caladium
#
#  Created by Declan Kelly on 20-01-2023.
#  Copyright © 2023 Declan Kelly. All rights reserved.
#

import json

import flask

import database

authorisation_tokens = []

class ClientRecord(database.DatabaseRecord):
    database_name = "clients"

clients = flask.Blueprint(__name__, "clients")

def get_authorisation_tokens():
    global authorisation_tokens
    return authorisation_tokens

def update_authorisation_tokens():
    global authorisation_tokens
    authorisation_tokens = [database.get(ClientRecord, client_id).get("token") for client_id in database.get_caladium_collection("clients")]

update_authorisation_tokens()

@clients.get("/api/clients")
def get_clients_route():
    return database.get_caladium_collection("clients")

@clients.post("/api/clients")
def create_clients_route():
    new_document = json.loads(flask.request.data.decode("utf-8"))
    resp_str = str(database.create(ClientRecord, new_document))
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
        client.delete()
    return {}

