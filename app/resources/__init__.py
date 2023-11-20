from flask import Blueprint

bp = Blueprint('resources', __name__, static_folder='static')

from app.resources import routes