from app.availability import bp
import app.availability.static.helpers.availability_functions as av
import app.availability.static.helpers.ram_functions as ram_funcs
from flask import render_template, request, jsonify, url_for, redirect, make_response
from celery import shared_task

@bp.route('/')
def index():
  return render_template('availability/index.html')

@bp.route('/packageuptime/')
def packageuptime():
  return render_template('availability/packageuptime.html')

@bp.route('/packageuptime/result/<task_id>', methods=["GET", "POST"])
def packageuptime_result(task_id):
  if request.method == "POST":
    #print(request.form)
    task = post_package_uptime_celery.apply_async(args = [request.form])
    return redirect(url_for('availability.task', task_id=task.id))
    
    #jsonify({}), 202, {'Location': url_for('availability.taskstatus',
    #                                              task_id=task.id)}
    #post_result = av.post_package_uptime(request=request)
    #return render_template('availability/packageuptime_result.html',
    #                       simulation_stats=post_result['stats'],
    #                      simulation_ts = post_result['ts'])
  else:
    task = post_package_uptime_celery.AsyncResult(task_id)
    post_result = task.result
    #print(post_result)
    return render_template('availability/packageuptime_result.html',
                           simulation_stats=post_result['stats'],
                          simulation_ts = post_result['ts'])


@bp.route('/ram/')
def ram():
  return render_template('availability/ram.html')


@bp.route('/rbd/')
def rbd():
  ex = ram_funcs.rbd_examples()
  config_file = ex["small"]["firewater"]

  rbd_file = ram_funcs.prepare_rbd(config_file = config_file)
  #print(rbd_file["config"]["x"])

  rbd_image = ram_funcs.draw_rbd_image(rbd_file["size"],rbd_file["config"])
  return render_template('availability/rbd.html', rbd_image = rbd_image)



@shared_task(bind=True, acks_late = True)
def post_package_uptime_celery(self,request_form):
  #print("test")
  result = av.post_package_uptime_v2(self,request_form=request_form)
  print("result collected")
  return result

@bp.route('/taskstatus/<task_id>')
def taskstatus(task_id):
  task = post_package_uptime_celery.AsyncResult(task_id)
  if task.state == 'PENDING':
    # job did not start yet
    response = {
        'state': task.state,
        'current': 0,
        'total': 1,
        'status': 'Pending...'
    }
  elif task.state != 'FAILURE':
    response = {
        'state': task.state,
        'current': task.info.get('current', 0),
        'total': task.info.get('total', 1),
        'status': task.info.get('status', '')
    }
    #print(task)
  else:
    # something went wrong in the background job
    response = {
        'state': task.state,
        'current': 1,
        'total': 1,
        'status': str(task.info),  # this is the exception raised
    }
  return jsonify(response)

@bp.route('/task/<task_id>')
def task(task_id):
  task = post_package_uptime_celery.AsyncResult(task_id)
  if task.state == 'SUCCESS':
    return redirect(url_for('availability.packageuptime_result', task_id=task_id))
  else:
    return render_template('tasks/task.html', task_status_url = url_for('availability.taskstatus',task_id=task_id))




