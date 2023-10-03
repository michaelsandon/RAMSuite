from app.survival import bp
from app.survival.static.helpers import survival_functions
import app.static.helpers.global_formatting_functions as gff
from flask import render_template, request, redirect, url_for



@bp.route('/')
def index():
  return render_template('survival/index.html')


@bp.route('/distsample/')
def distsample():
  return render_template('survival/distsample.html')

@bp.route('/distsample/result', methods=["GET", "POST"])
def distsample_result():
  
  params = {
    'param1':request.form['param1'],
    'param2':request.form['param2'],
    'param3':request.form['param3']
  }
  #perform sampling and generate histogram
  sampling_results = survival_functions.sampling(
    dist=request.form['dist'],
    params=gff.helper_formdata_to_list(params),
    n_samples=eval(request.form['n_samples']),
    html = True)
  
  return render_template('survival/distsample_result.html',
                        samples = sampling_results['samples'],
                        histogram = sampling_results['histogram'])

@bp.route('/survivalfit/')
def survivalfit():
  return render_template('survival/survivalfit.html')


@bp.route('/survivalfit/result/', methods=["GET", "POST"])
def survivalfit_result():
  if request.method == "GET":
    return render_template('survival/survivalfit_result.html')
  else:
    #convert form request to input dictionary and then to dataframe
    observed_life_data_dict = {
      'time': request.form['survivaltimes'],
      'censor': request.form['survivalcensor'],
      'qty': request.form['survivalqty']
    }
    observed_life_data_df = gff.helper_formdata_to_df(
      form_data=observed_life_data_dict)

    #manage checkboxes
    plot_options = {}
    for plotkey in ['probability_plot', 'sf_plot', 'km_plot']:
      if plotkey in request.form:
        plot_options[plotkey] = True
      else:
        plot_options[plotkey] = False

    #perform analysis
    analysis_results = survival_functions.survival_analysis(
      life_data=observed_life_data_df,
      grouped=True,
      output="html",
      method=request.form['fitmethod'],
      plot_options = plot_options)

    return render_template('survival/survivalfit_result.html',
                           data=analysis_results['Datatables'],
                           plots=analysis_results['Plots'])
