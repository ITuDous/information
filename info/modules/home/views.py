from . import home_blu
from flask import current_app


@home_blu.route('/')
def index():
    return "index"
