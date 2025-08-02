from flask import (Blueprint, redirect, render_template, request, session,
                   url_for)
from flask_socketio import emit

from ..database.db import member
from ..database.exceptions import ElementDoesNotExsist

scanner_site = Blueprint(
    "scanner", __name__, template_folder="templates", url_prefix="/scanner")


@scanner_site.get("/")
def configure():
    return render_template("scanner/configure.html")


@scanner_site.get("/scanner")
def scanner():
    return render_template("scanner/scanner.html")
