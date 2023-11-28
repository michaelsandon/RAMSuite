from app.maintenance import bp
from flask import render_template, jsonify, request, redirect, url_for
import app.maintenance.static.helpers.maint_db_functions as maint_db_funcs


def models():
  models = maint_db_funcs.helper_query_fmea_by_id(tables=["doc"],format="scalars")
  return models

@bp.route('/')
def index():
  return render_template('maintenance/index.html', parent_map_index = 4)

@bp.route('/strategysimulator')
def strategysimulator():
  return jsonify('under dev')

@bp.route('/strategyoptimiser')
def strategy_optimiser():
  return jsonify('under dev')

@bp.route('/fmea')
def fmea():
  return render_template('maintenance/fmea/fmea.html', models = models())


@bp.route('/fmea/modelmanager/', methods=["GET","POST"])
@bp.route('/fmea/modelmanager/<model_id>/', methods=["GET","POST"])
def fmea_model_manager(model_id=None):
  if (request.method == "POST") & (model_id is None):
    #get model id from request
    model_id = int(request.form["modelselect"])
    #run some error checkinf
    if model_id is None:
      #other error checking to be added
      return render_template('maintenance/fmea/fmea.html', models = models())
    else:
      return redirect(url_for('maintenance.fmea_model_manager', model_id = model_id))#, code=307)

  else:
    model_html = maint_db_funcs.helper_query_fmea_by_id(fmeaid=model_id, format="html-std")
    model_details = maint_db_funcs.helper_query_fmea_by_id(fmeaid=model_id, format="scalars")

    tbls = {
      "Functions":model_html["functions"],
      "Functional Failures":model_html["functionalfailures"],
      "Functional Failure Consequences":model_html["functionalfailureconsequences"],
      "Failure Modes":model_html["failuremodes"],
      "Failure Map":model_html["failuremap"]
        }

    fmea = maint_db_funcs.helper_query_combined_fmea_by_id(fmeaid = model_id, format = "html-std", grouped=True)

    return render_template('maintenance/fmea/fmea_model_manager.html',
                           model_index = model_details["doc"].one(),
                           functions = model_details["functions"],
                           tbls = tbls,
                           fmea = fmea
                          )


@bp.route('/fmea/model/<fmea_id>/all')
def api_fmea_model_all(fmea_id):
  response = maint_db_funcs.helper_query_fmea_by_id(fmeaid=fmea_id)
  return response

@bp.route('/fmea/model/<fmea_id>/detail/<table>/')
@bp.route('/fmea/model/<fmea_id>/detail/<table>/<datatype>')
def api_fmea_model_detail(fmea_id, table, datatype = None):

  response = maint_db_funcs.helper_query_fmea_by_id(tables=[table], fmeaid=fmea_id, format=datatype)

  return response

@bp.route('/fmea/create/<table>/', methods=["POST"])
def create_fmea_record(table):
  if table == "fmea_index":
    new_fmea_id = maint_db_funcs.create_fmea_record("fmea_index",request.form)
    response = redirect(url_for('maintenance.fmea_model_manager', model_id = new_fmea_id))
  else:
    pass

  return response
  
  