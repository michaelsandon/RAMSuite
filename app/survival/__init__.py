from flask import Blueprint

bp = Blueprint('survival', __name__, static_folder='static')

from app.survival import routes