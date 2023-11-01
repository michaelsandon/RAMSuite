from app.availability import bp
import app.availability.static.helpers.availability_functions as av
import app.availability.static.helpers.ram_functions as ram_funcs
import app.availability.static.helpers.ram_db_functions as ram_db_funcs
import app.static.helpers.global_formatting_functions as gff
import app.static.helpers.global_reliability_helpers as grh

from flask import render_template, request, jsonify, url_for, redirect

from app.tasks.shared_tasks import celery_task_router

import pandas as pd


@bp.route('/')
def index():
  return render_template('availability/index.html')

@bp.route('/packageuptime/')
def packageuptime():
  return render_template('availability/packageuptime.html')

@bp.route('/packageuptime/result/', methods=["POST"])
@bp.route('/packageuptime/result/<task_id>', methods=["GET"])
def packageuptime_result(task_id=None):
  if request.method == "POST":
    task = celery_task_router.apply_async(args = [request.form,"av-pu", 'availability.packageuptime_result'])
    return redirect(url_for('tasks.task', task_id=task.id))
    
  else:
    
    task = celery_task_router.AsyncResult(task_id)
    task_result = task.result
    return render_template('availability/packageuptime_result.html',
                           simulation_stats=task_result['stats'],
                          simulation_ts = task_result['ts'])


@bp.route('/ram/')
def ram():
  models = ram_db_funcs.helper_query_ram_model_db_by_model_id(tables=["model"],format="scalars")
  return render_template('availability/ram.html', models = models)

@bp.route('/ram/result/', methods=["POST"])
@bp.route('/ram/result/<task_id>', methods=["GET"])
def ram_result(task_id = None):
  if request.method == "POST":
    task = celery_task_router.apply_async(args = [request.form,"av-ram",'availability.ram_result'])
    return redirect(url_for('tasks.task', task_id=task.id))

  else:
    task = celery_task_router.AsyncResult(task_id)
    task_result = task.result
    links = gff.helper_add_links_to_frame_as_html(task_id = task_id, n_sims = task_result["n_sims"])
    return render_template('availability/ram_result.html', 
                           times = task_result["times"], 
                           av = task_result["av"],
                           av_stats = task_result["av_stats"],
                           inv = task_result["inv"],
                           inv_stats = task_result["inv_stats"],
                           eq_crit = task_result["eq_crit"],
                           eq_crit_stats = task_result["eq_crit_stats"],
                           links = links)




@bp.route('/ram/result/<task_id>/simdetail/<sim_id>', methods=["GET"])
def ram_sim_result(task_id,sim_id):
  task = celery_task_router.AsyncResult(task_id)
  task_result = task.result
  sim_result = task_result["details"][int(sim_id)]

  uptime_plt = grh.helper_plot_time_based_df_as_html_image(pd.read_json(sim_result["FM_lifetimes"]))
  inv_plt = grh.helper_plot_time_based_df_as_html_image(pd.read_json(sim_result["inventory_lifetimes"]))
  logs = gff.helper_format_df_as_std_html(pd.read_json(sim_result["Event_log_all"]))
  return render_template('availability/ram_sim_result.html', 
                        task_id = task_id, sim_id = sim_id, uptime_plt = uptime_plt, inv_plt = inv_plt, logs = logs)
  
@bp.route('/ram/model/<model_id>/all')
def api_ram_model_all(model_id):
  response = ram_db_funcs.helper_query_ram_model_db_by_model_id(modelid=model_id)
  return response

@bp.route('/ram/model/<model_id>/detail/<table>/')
@bp.route('/ram/model/<model_id>/detail/<table>/<datatype>')
def api_ram_model_detail(model_id, table, datatype = None):

  response = ram_db_funcs.helper_query_ram_model_db_by_model_id(tables=[table], modelid=model_id,format=datatype)

  return response

@bp.route('/ram/model/<model_id>/subsystems/')
def content_ram_model_subsystems(model_id, datatype = None):

  ssindex = ram_db_funcs.helper_query_ram_model_db_by_model_id(tables=["subsystemindex"], modelid=model_id,format="df")
  ssstruc = ram_db_funcs.helper_query_ram_model_db_by_model_id(tables=["subsystemstructure"], modelid=model_id,format="df")

  if len(ssstruc)>0:
    response = gff.helper_format_parent_child_dfs_as_html(dfparent = ssindex, dfchild=ssstruc, parentidcol="id",childparentidcol="subsystemid")
  else:
    response = gff.helper_format_df_as_std_html(ssstruc)
  #q = ramdb.select(rmss,rmsi).join(rmsi).join(rmi).where(rmi.id==model_id)
  return response


@bp.route('/ram/model/<model_id>/rbd/')
@bp.route('/ram/model/<model_id>/rbd/<image>')
def model_rbd(model_id,image = None):

  eqdf = ram_db_funcs.helper_query_ram_model_db_by_model_id(tables=["equipment"], modelid=model_id,format="df")
  subsysdf = ram_db_funcs.helper_query_ram_model_db_by_model_id(tables=["subsystemstructure"], modelid=model_id,format="df")
  sysdf = ram_db_funcs.helper_query_ram_model_db_by_model_id(tables=["system"], modelid=model_id,format="df")

  compiled_sys = ram_funcs.compile_system_hierarchy(equipmentdf=eqdf,
                                             subsystemdf=subsysdf,
                                             systemdf=sysdf)

  if image is not None:
    rbd_file = ram_funcs.prepare_rbd(config_file = compiled_sys)
    rbd_image = ram_funcs.draw_rbd_image(rbd_file["size"],rbd_file["config"])
    response = render_template('availability/rbd.html', rbd_image = rbd_image)
  else:
    rbd_file = ram_funcs.prepare_rbd(config_file = compiled_sys)
    response = gff.helper_format_df_as_std_html(rbd_file["config"])#compiled_sys)
  return response
  #return gff.helper_format_df_as_std_html(compiled_sys)



