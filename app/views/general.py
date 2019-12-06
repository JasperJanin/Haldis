"Script to generate the general views of Haldis"
import os
from datetime import datetime, timedelta

import yaml

from flask import Flask, render_template, make_response
from flask import request
from flask import Blueprint, abort
from flask import current_app as app
from flask import send_from_directory, url_for
from flask_login import login_required

from models import Location, Order
# import views
from views.order import get_orders

general_bp = Blueprint("general_bp", __name__)


@general_bp.route("/")
def home() -> str:
    "Generate the home view"
    prev_day = datetime.now() - timedelta(days=1)
    recently_closed = get_orders(
        ((Order.stoptime > prev_day) & (Order.stoptime < datetime.now()))
    )
    return render_template(
        "home.html", orders=get_orders(), recently_closed=recently_closed
    )


@general_bp.route("/css")
def css():
    "Generate the css"
    if request.cookies.get('performance', '') == 'highPerformance':
        cssPath = 'static/css/themes/highPerformance/'
    else:
        cssPath = 'static/css/themes/lowPerformance/'

    cookie_theme = request.cookies.get('theme', '')
    if cookie_theme == 'customTheme':
        #TODO: The custom theme is hardcoded :(. Make the server auto select a custom team.
        # Here seasonal themes will be returned; matching the current date.

        # Open the YAML file with all the themes.
        path = os.path.join(app.root_path, "views/themes.yml")
        with open(path, 'r') as stream:
            data = yaml.safe_load(stream)
        # Build a dictionary from the YAML file with all the themes and there attributes.
        themes = {}
        for item in data:
            key = list(item.keys())[0]
            themes[key] = item[key]

        # Get the current date.
        current_date = datetime.now()
        current_year = current_date.year

        # Check each theme in the dictionary and return the first one that is "correct"
        for theme in themes.values():
            if theme['type'] == 'static-date':
                start_day, start_month = theme['start'].split('/')
                start_date = datetime(year=current_year, day=int(
                    start_day), month=int(start_month))

                end_day, end_month = theme['end'].split('/')
                if int(start_month) > int(end_month):
                    current_year += 1
                end_date = datetime(
                    year=current_year, day=int(end_day), month=int(end_month))

                if start_date <= current_date <= end_date:
                    path = os.path.join(app.root_path, cssPath, theme['file'])
                    break
    elif cookie_theme == 'darkmode':
        path = os.path.join(
            app.root_path, "static/css/themes/lowPerformance/darkmode.css")
    else:
        path = os.path.join(
            app.root_path, "static/css/themes/lowPerformance/lightmode.css")

    f = open(path)
    response = make_response(f.read())
    response.headers['Content-Type'] = 'text/css'
    f.close()
    return response


@general_bp.route("/map")
def map_view() -> str:
    "Generate the map view"
    locs = Location.query.order_by("name")
    return render_template("maps.html", locations=locs)


@general_bp.route("/location")
def locations() -> str:
    "Generate the location view"
    locs = Location.query.order_by("name")
    return render_template("locations.html", locations=locs)


@general_bp.route("/location/<int:location_id>")
def location(location_id) -> str:
    "Generate the location view given an id"
    loc = Location.query.filter(Location.id == location_id).first()
    if loc is None:
        abort(404)
    return render_template("location.html", location=loc, title=loc.name)


@general_bp.route("/about/")
def about() -> str:
    "Generate the about view"
    return render_template("about.html")


@general_bp.route("/profile/")
@login_required
def profile() -> str:
    "Generate the profile view"
    return render_template("profile.html")


@general_bp.route("/favicon.ico")
def favicon() -> str:
    "Generate the favicon"
    # pylint: disable=R1705
    if not get_orders((Order.stoptime > datetime.now())):
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon.ico",
            mimetype="image/x-icon",
        )
    else:
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "favicon_orange.ico",
            mimetype="image/x-icon",
        )
