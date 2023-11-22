from app.maintenance import bp
from flask import render_template, jsonify

@bp.route('/')
def index():
  return jsonify('under dev')


@bp.route('/strategysimulator')
def strategysimulator():
  return jsonify('under dev')

@bp.route('/strategyoptimiser')
def strategy_optimiser():
  return jsonify('under dev')

@bp.route('/fmea')
def fmea():
  return render_template('maintenance/fmea.html')