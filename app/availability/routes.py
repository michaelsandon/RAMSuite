from app.availability import bp
import app.availability.static.helpers.availability_functions as av
from flask import render_template, request


@bp.route('/')
def index():
  return render_template('availability/index.html')


@bp.route('/packageuptime/')
def packageuptime():
  return render_template('availability/packageuptime.html')


@bp.route('/packageuptime/result', methods=["GET", "POST"])
def packageuptime_result():
  if request.method == "POST":
    print(request.form)
    post_result = av.post_package_uptime(request=request)
    return render_template('availability/packageuptime_result.html',
                           simulation_stats=post_result['stats'],
                          simulation_ts = post_result['ts'])
  else:
    return render_template('availability/packageuptime_result.html')
