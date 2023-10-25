from app.main import bp
from flask import render_template, request, jsonify, url_for, redirect


@bp.route('/')
def index():
  return render_template('index.html')