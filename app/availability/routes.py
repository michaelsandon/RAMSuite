from app.availability import bp
import app.availability.static.helpers.availability_functions as av
import app.availability.static.helpers.ram_functions as ram_funcs
import app.availability.static.helpers.ram_db_functions as ram_db_funcs
import app.static.helpers.global_formatting_functions as gff
import app.static.helpers.global_reliability_helpers as grh

from flask import render_template, request, jsonify, url_for, redirect

from app.tasks.shared_tasks import celery_task_router

import pandas as pd

def models():
  models = ram_db_funcs.helper_query_ram_model_db_by_model_id(tables=["model"],format="scalars")
  return models

@bp.route('/')
def index():
  return render_template('availability/index.html', parent_map_index = 2)

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
  return render_template('availability/ram.html', models = models())

@bp.route('/ram/modelmanager/', methods=["POST"])
@bp.route('/ram/modelmanager/<model_id>/', methods=["POST"])
def ram_model_manager(model_id=None):
  if (request.method == "POST") & (model_id is None):
    #get model id from request
    model_id = int(request.form["rammodelselect"])
    #run some error checkinf
    if model_id is None:
      #other error checking to be added
      return render_template('availability/ram.html', models = models())
    else:
      return redirect(url_for('availability.ram_model_manager', model_id = model_id), code=307)

  else:
    model = ram_db_funcs.helper_query_ram_model_db_by_model_id(modelid=model_id, format="html-std")
    model_details = ram_db_funcs.helper_query_ram_model_db_by_model_id(modelid=model_id, format="df", tables=["model"])

    mapped_accordion = {
      "Equipment Index":model["equipment"],
      "Sub-Systems":model["subsystemstructure"],
      "System":model["system"],
      "Equipment Failure Modes":model["failuremodes"],
      "Failuremode Responses":model["equipmentfailuremoderesponses"],
      "Inspection":None,
      "Condition Based Maintenance":model["conditionbasedmaintenance"],
      "Time Based Maintenance":None,
      "Inventory":model["inventory"],
      "Maintenance Task Lists":model["componentlistdetails"],
      "Integrated / Planned Shutdown Events":None,
      "Conditional Logic":None,
      "Operational Responses":None,
      "Capital Upgrade Responses":None
        }
    
    return render_template('availability/ram_model_manager.html',
                           model_id = model_details.loc[0,"id"],
                           loaded_model_title = model_details.loc[0,"title"],
                           mapped_accordion = mapped_accordion
                          )


@bp.route('/ram/result/', methods=["POST"])
@bp.route('/ram/result/<task_id>', methods=["GET"])
def ram_result(task_id = None):
  if request.method == "POST":
    task = celery_task_router.apply_async(args = [request.form,"av-ram",'availability.ram_result'])
    return redirect(url_for('tasks.task', task_id=task.id))

  else:
    task = celery_task_router.AsyncResult(task_id)
    task_result = task.result
    links = gff.helper_add_links_to_frame_as_html(task_id = task_id, n_sims = task_result["n_sims"], table_id="links")
    return render_template('availability/ram_result.html', 
                           times = task_result["times"], 
                           Sys_Av_Stats = task_result["Sys_Av_Stats"],
                           prod_plot = task_result["plots"]["production_plot"],
                           Eq_Av_Stats = task_result["Eq_Av_Stats"],
                           Inv_Stats = task_result["Inv_Stats"],
                           Eq_Crit_Stats = task_result["Eq_Crit_Stats"],
                           Maint_Stats = task_result["Maint_Stats"],
                           links = links)




@bp.route('/ram/result/<task_id>/simdetail/<sim_id>', methods=["GET"])
def ram_sim_result(task_id,sim_id):
  task = celery_task_router.AsyncResult(task_id)
  task_result = task.result

  sim_results = ram_funcs.return_model_results_by_sim_id(compiled_results = task_result,sim_id = sim_id)

  return render_template('availability/ram_sim_result.html', 
                        task_id = task_id,
                         sim_id = sim_id,
                         Sys_Av = sim_results["Sys_Av"],
                         Eq_Av = sim_results["Eq_Av"],
                         Inv= sim_results["Inv"],
                         Eq_Crit = sim_results["Eq_Crit"],
                         uptime_plt = sim_results["uptime_plt"],
                         inv_plt = sim_results["inv_plt"],
                         ev_log = sim_results["ev_log"])
  
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


    
@bp.route('/ram/rbd/', methods=["POST"])
@bp.route('/ram/rbd/<model_id>/', methods=["POST"])
def ram_model_rbd(model_id=None):
  if (request.method == "POST") & (model_id is None):
    #get model id from request
    model_id = int(request.form["model_id"])
    #run some error checkinf
    if model_id is None:
      #other error checking to be added
      return render_template('availability/ram.html', models = models())
    else:
      return redirect(url_for('availability.ram_model_rbd', model_id = model_id), code=307)

  else:
    eqdf = ram_db_funcs.helper_query_ram_model_db_by_model_id(tables=["equipment"], modelid=model_id,format="df")
    subsysdf = ram_db_funcs.helper_query_ram_model_db_by_model_id(tables=["subsystemstructure"], modelid=model_id,format="df")
    sysdf = ram_db_funcs.helper_query_ram_model_db_by_model_id(tables=["system"], modelid=model_id,format="df")
  
    compiled_sys = ram_funcs.compile_system_hierarchy(equipmentdf=eqdf,
                                               subsystemdf=subsysdf,
                                               systemdf=sysdf)

    rbd_file = ram_funcs.prepare_rbd(config_file = compiled_sys)
    rbd_image = ram_funcs.draw_rbd_image(rbd_file["size"],rbd_file["config"])
    response = render_template('availability/rbd.html', rbd_image = rbd_image)

  return response
  #return gff.helper_format_df_as_std_html(compiled_sys)



