from flask import (Blueprint, Flask, redirect, render_template, request,
                   send_file, session, url_for)
from flask_socketio import emit
from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import qr
from reportlab.graphics.shapes import Drawing
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from ..database.db import member, stufe
from ..database.exceptions import ElementDoesNotExsist

admin_site = Blueprint(
    "admin", __name__, template_folder="templates", url_prefix="/admin")


@admin_site.route("/users")
def users():
    """
    Render the users page with a list of all members.
    """

    members = member.get_all()

    stufen = stufe.get_all()

    return render_template("admin/users.html",
                           members=[m.to_dict() for m in members],
                           stufen=[s.to_dict() for s in stufen])
