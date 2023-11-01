from flask import Blueprint

bp = Blueprint('examples', __name__, static_folder='static')

from app.examples import routes