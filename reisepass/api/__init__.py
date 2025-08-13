import json

from flask import (Blueprint, abort, redirect, render_template, request,
                   session, url_for)

from reisepass import socketio

from ..database.db import member
from ..database.exceptions import ElementDoesNotExsist

api = Blueprint("api", __name__, template_folder="templates",
                url_prefix="/api")


@api.errorhandler(ElementDoesNotExsist)
def handle_element_does_not_exist(error):
    return "NOT FOUND", 404


@api.post("/scan/<int:scanner_id>")
def scan(scanner_id: int):
    try:
        code = dict(json.loads(request.data)).get("data")
        mem = member.get_via_code(code)
    except ElementDoesNotExsist:
        return f"Member with code {code} not found", 404
    except json.JSONDecodeError:
        print("Invalid JSON data received")
        abort(400, description=f"Invalid JSON format {request.data}")
    print(f"Emitting to scanner{scanner_id} with {mem.to_dict()}")
    socketio.emit(f"scaner{scanner_id}", {"member": mem.to_dict()})
    return "OK", 200


@api.get("/member/<int:member_id>")
def get_member(member_id: int):
    try:
        mem = member.get_via_id(member_id)
        return mem.to_dict()
    except ElementDoesNotExsist:
        abort(404)


@api.get("/member/code/<string:code>")
def get_member_by_code(code: str):
    try:
        mem = member.get_via_code(code)
        return mem.to_dict()
    except ElementDoesNotExsist:
        abort(404)
