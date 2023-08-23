from app.availability import bp
from app.survival.static.helpers import survival_functions
from flask import render_template, request, redirect, url_for
from json import loads


@bp.route('/')
def index():
  return render_template('availability/index.html')

@bp.route('/packageuptime/')
def packageuptime():
  return render_template('availability/packageuptime.html')

