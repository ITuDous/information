from flask import Blueprint

passport_blu = Blueprint("passport", __name__)

from .views import *
