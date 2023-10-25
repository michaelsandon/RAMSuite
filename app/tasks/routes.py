from app.tasks import bp
from app.tasks.shared_tasks import celery_task_router
from flask import render_template, request, jsonify, url_for, redirect

@bp.route('/taskstatus/<task_id>')
def taskstatus(task_id):
  task = celery_task_router.AsyncResult(task_id)
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
  task = celery_task_router.AsyncResult(task_id)
  if task.state == 'SUCCESS':
    print(task)
    print(task.args)
    return redirect(url_for('availability.packageuptime_result', task_id=task_id))
  else:
    return render_template('tasks/task.html', task_status_url = url_for('tasks.taskstatus',task_id=task_id))