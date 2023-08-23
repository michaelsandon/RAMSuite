from flask import Blueprint

bp = Blueprint('availability', __name__, static_folder='static')

from app.availability import routes