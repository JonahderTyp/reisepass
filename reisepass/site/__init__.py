from flask import Blueprint, redirect, render_template, session, url_for

from ..database.exceptions import ElementDoesNotExsist
from .card import card_site
from .display import display_site
from .scanner import scanner_site

site = Blueprint("site", __name__, template_folder="templates")


site.register_blueprint(scanner_site)
site.register_blueprint(card_site)
site.register_blueprint(display_site)


@site.errorhandler(ElementDoesNotExsist)
def handle_element_does_not_exist(error):
    return render_template("error.html", error=error, code=404), 404


@site.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


@site.route("/")
def index():
    return render_template("index.html")
