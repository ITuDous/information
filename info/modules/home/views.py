from . import home_blu
from flask import current_app, render_template


@home_blu.route('/')
def index():
    return render_template("index.html")


@home_blu.route('/favicon.ico')
def favicon():
    return current_app.send_static_file("news/favicon.ico")
