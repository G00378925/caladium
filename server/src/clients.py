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

class ClientRecord(database.DatabaseRecord):
    database_name = "clients"

clients = flask.Blueprint(__name__, "clients")

@clients.get("/api/clients")
def get_clients_route():
    return database.get_caladium_collection("clients")

@clients.post("/api/clients")
def create_clients_route():
    new_document = json.loads(flask.request.data.decode("utf-8"))
    return str(database.create(ClientRecord, new_document))

@clients.delete("/api/clients/<client_id>")
def delete_client_route(client_id):
    if client := database.get(ClientRecord, client_id):
        client.delete()
    return {}

