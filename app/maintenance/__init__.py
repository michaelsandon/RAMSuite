from flask import Blueprint

bp = Blueprint('maintenance',__name__,static_folder='static')

from app.maintenance import routes