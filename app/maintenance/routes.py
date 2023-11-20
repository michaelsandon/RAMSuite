from app.maintenance import bp
from flask import render_template, jsonify

@bp.route('/')
def index():
  return jsonify('under dev')
  