from flask import Blueprint

bp = Blueprint('tasks', __name__, static_folder='static')

from app.tasks import routes