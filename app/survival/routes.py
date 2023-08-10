from app.survival import bp
from app.survival.static.helpers import survival_functions
from flask import render_template, request, redirect, url_for
from json import loads


@bp.route('/')
def index():
  return render_template('survival/index.html')


@bp.route('/sample/')
def sample():
  return render_template('survival/index.html')


@bp.route('/weibullfit/')
def weibullfit():
  return render_template('survival/weibullfit.html')


@bp.route('/weibullfit/result/', methods=["GET", "POST"])
def weibullfit_result():
  if request.method == "GET":
    return render_template('survival/weibullfit_result.html')
  else:
    #convert form request to input dictionary and then to dataframe
    observed_life_data_dict = {
      'time': request.form['survivaltimes'],
      'censor': request.form['survivalcensor'],
      'qty': request.form['survivalqty']
    }
    observed_life_data_df = survival_functions.helper_formdata_to_df(
      form_data=observed_life_data_dict)

    #manage checkboxes
    plots_options = {}
    for plotkey in ['probability_plot', 'sf_plot', 'mle_plot']:
      if plotkey in request.form:
        plots_options[plotkey] = True
      else:
        plots_options[plotkey] = False

    #perform analysis
    analysis_results = survival_functions.survival_analysis(
      life_data=observed_life_data_df,
      grouped=True,
      output="html",
      method=request.form['fitmethod'])

    return render_template('survival/weibullfit_result.html',
                           method="post",
                           data=analysis_results['Datatables'],
                           plots=analysis_results['Plots'])
