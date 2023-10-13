from app.availability import bp
import app.availability.static.helpers.availability_functions as av
import app.availability.static.helpers.ram_functions as ram_funcs
from app.models.ram import ram_model_index as rmi, ram_model_equipment as rme, ram_model_subsystem_index as rmsi, ram_model_subsystem_structure as rmss, ram_model_system_structure as rms
from app.extensions import ramdb
from sqlalchemy import select
from flask import render_template, request, jsonify, url_for, redirect, make_response
from celery import shared_task
import pandas as pd
import app.static.helpers.global_formatting_functions as gff

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
  models = ramdb.session.scalars(ramdb.select(rmi))
  return render_template('availability/ram.html', models = models)

@bp.route('/ram/model/<model_id>')
def loadrammodel(model_id):
  if model_id == '0':
    ex = ram_funcs.rbd_examples()
    model = ex["deconstructed"]["firewater"]
    response = model.to_json()
  else:
    #model = ram_model_index.query.get_or_404(model_id)
    query1 = ramdb.select(rmi).where(rmi.id==model_id)
    query2 = ramdb.select(rme).join(rmi).where(rmi.id==model_id)
    query3 = ramdb.select(rmsi).join(rmi).where(rmi.id == model_id)
    query4 = ramdb.select(rmss).join(rmsi).join(rmi).where(rmi.id==model_id)
    conn = ramdb.session.connection()
    response = {}
    counter = 0
    for q in [query1,query2,query3,query4]:
      counter = counter+1
      response["q"+str(counter)]= pd.read_sql(q,conn).to_dict()
    
  return response

@bp.route('/ram/model/<model_id>/index/')
@bp.route('/ram/model/<model_id>/index/<datatype>')
def api_ram_model_index(model_id, datatype = None):
  q = ramdb.select(rmi).where(rmi.id==model_id)
  conn = ramdb.session.connection()

  df = pd.read_sql(q,conn)

  if datatype == "html":
    response = gff.helper_format_df_as_std_html(df)
  else:
    response = df.to_dict(orient='records')[0]
    
  return response

@bp.route('/ram/model/<model_id>/equipment/')
@bp.route('/ram/model/<model_id>/equipment/<datatype>')
def api_ram_model_equipment(model_id, datatype = None):
  q = ramdb.select(rme).join(rmi).where(rmi.id==model_id)
  conn = ramdb.session.connection()

  df = pd.read_sql(q,conn)

  if datatype == "html":
    response = gff.helper_format_df_as_std_html(df)
  else:
    response = df.to_dict()
    
  return response

@bp.route('/ram/model/<model_id>/subsystems/')
@bp.route('/ram/model/<model_id>/subsystems/<datatype>')
def api_ram_mpdel_subsystems(model_id, datatype = None):

  conn = ramdb.session.connection()

  if datatype == "html":
    q = ramdb.select(rmss,rmsi).join(rmsi).join(rmi).where(rmi.id==model_id)
    df = pd.read_sql(q,conn)
    response = gff.helper_format_df_as_std_html(df)
  elif datatype == "html-comp":
    q2 = ramdb.select(rmss).join(rmsi).join(rmi).where(rmi.id==model_id)
    q1 = ramdb.select(rmsi).join(rmi).where(rmi.id==model_id)
    df1 = pd.read_sql(q1,conn)
    df2 = pd.read_sql(q2,conn)
    if len(df2)>0:
      response = gff.helper_format_parent_child_dfs_as_html(dfparent = df1, dfchild=df2, parentidcol="id",childparentidcol="subsystemid")
    else:
      response = gff.helper_format_df_as_std_html(df2)
      
  else:
    q = ramdb.select(rmss,rmsi).join(rmsi).join(rmi).where(rmi.id==model_id)
    df = pd.read_sql(q,conn)
    response = df.to_dict()
    
  return response


@bp.route('/ram/model/<model_id>/system/')
@bp.route('/ram/model/<model_id>/system/<datatype>')
def api_ram_model_system(model_id, datatype = None):
  q = ramdb.select(rms).join(rmi).where(rmi.id==model_id)
  conn = ramdb.session.connection()
  df = pd.read_sql(q,conn)
  if datatype == "html":
    response = gff.helper_format_df_as_std_html(df)
  else:
    response = df.to_dict()
    
  return response


@bp.route('/rbd/')
def rbd():
  ex = ram_funcs.rbd_examples()
  config_file = ex["small"]["firewater"]

  rbd_file = ram_funcs.prepare_rbd(config_file = config_file)
  #print(rbd_file["config"]["x"])

  rbd_image = ram_funcs.draw_rbd_image(rbd_file["size"],rbd_file["config"])
  return render_template('availability/rbd.html', rbd_image = rbd_image)


@bp.route('/ram/model/<model_id>/rbd/')
@bp.route('/ram/model/<model_id>/rbd/<image>')
def model_rbd(model_id,image = None):
  q1 = ramdb.select(rme).join(rmi).where(rmi.id==model_id)
  q2 = ramdb.select(rmss).join(rmsi).join(rmi).where(rmi.id == model_id)
  q3 = ramdb.select(rms).join(rmi).where(rmi.id==model_id)
  conn = ramdb.session.connection()

  eqdf = pd.read_sql(q1,conn)
  subsysdf = pd.read_sql(q2,conn)
  sysdf = pd.read_sql(q3,conn)

  compiled_sys = ram_funcs.compile_ram_system(equipmentdf=eqdf,
                                             subsystemdf=subsysdf,
                                             systemdf=sysdf)

  if image is not None:
    rbd_file = ram_funcs.prepare_rbd(config_file = compiled_sys)
    #print(rbd_file["config"]["x"])
  
    rbd_image = ram_funcs.draw_rbd_image(rbd_file["size"],rbd_file["config"])
    response = render_template('availability/rbd.html', rbd_image = rbd_image)
  else:
    rbd_file = ram_funcs.prepare_rbd(config_file = compiled_sys)
    response = gff.helper_format_df_as_std_html(rbd_file["config"])#compiled_sys)
  return response
  #return gff.helper_format_df_as_std_html(compiled_sys)

@shared_task(bind=True, acks_late = True)
def post_package_uptime_celery(self,request_form):
  #print("test")
  result = av.post_package_uptime_v2(self,request_form=request_form)
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




