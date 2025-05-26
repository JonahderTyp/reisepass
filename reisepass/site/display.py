from flask import (Blueprint, redirect, render_template, request, session,
                   url_for)
from flask_socketio import emit

from ..database.db import member
from ..database.exceptions import ElementDoesNotExsist

display_site = Blueprint(
    "display", __name__, template_folder="templates", url_prefix="/display")


@display_site.get("/")
def display():
    return render_template("display/display.html")
