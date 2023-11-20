import matplotlib

matplotlib.use('agg')

import matplotlib.pyplot as plt
import reliability.Distributions as reldist
import reliability.Fitters as relfit
import reliability.Probability_plotting as relplot
import reliability.Nonparametric as relnp
import reliability.Other_functions as reloth
import pandas as pd
import app.static.helpers.global_formatting_functions as gff


def sampling(dist="Weibull_Distribution",
             params=[30, 1.5, None],
             n_samples=30,
             histogram=True,
             html=True):

  #acquire dist
  dist_func = getattr(reldist, dist)
  try:
    dist = dist_func(params[0], params[1], params[2])
  except:
    try:
      dist = dist_func(params[0], params[1])
    except:
      dist = dist_func(params[0])

  #get samples
  samples = dist.random_samples(n_samples)
  samples_df = pd.DataFrame(samples, columns=['Lifetime'])

  if html:
    sampleresult = gff.helper_format_df_as_std_html(samples_df)
  else:
    sampleresult = samples_df

  #histogram
  plot_png = None
  if histogram:
    reloth.histogram(samples)
    plot_png = gff.helper_save_curr_plt_as_byte()

  return {'samples': sampleresult, 'histogram': plot_png}


def survival_analysis(life_data,
                      grouped=False,
                      output="html",
                      method="Weibull_2P",
                      plot_options={
                        'probability_plot': True,
                        'sf_plot': True,
                        'km_plot': True
                      },
                     updates = None):

  #clean up df if needed
  life_data = life_data.fillna(value={'qty': 1, 'censor': False})
  life_data = life_data[life_data['time'].notnull()]

  #transform life data if needed from grouped to single obs
  if (grouped):
    life_data = pd.DataFrame(life_data.values.repeat(life_data.qty, axis=0),
                             columns=life_data.columns).drop('qty', axis=1)

  #perform analysis
  if updates is not None:
    self = updates[0]
    meta = updates[1]
    meta.update({"status":"Fitting Survival Distribution(s)","current":1})
    self.update_state(state='PROGRESS', meta= meta)
    
  fit_func = getattr(relfit, "Fit_" + method)
  #plt.subplot(121)
  fit = fit_func(
    failures=(life_data['time'][life_data['censor'] != True]).to_list(),
    right_censored=(life_data['time'][life_data['censor'] == True]).to_list(),
    show_probability_plot=False,
    print_results=False,
    downsample_scatterplot=False)

  #store results
  result = fit.results

  #generate and store plots
  if updates is not None:
    meta.update({"status":"Producing selected plots","current":2})
    self.update_state(state='PROGRESS', meta= meta)
    
  plots = {}

  for key, plotitem in plot_options.items():
    if plotitem:
      plotted = False
      fig = plt.figure()
      try:
        match key:
          case 'probability_plot':
            fit_func(
              failures=(
                life_data['time'][life_data['censor'] != True]).to_list(),
              right_censored=(
                life_data['time'][life_data['censor'] == True]).to_list(),
              show_probability_plot=True,
              print_results=False,
              downsample_scatterplot=False,
              figure = fig
            )
            plotted = True
          case 'sf_plot':
            fit.distribution.SF(label='Fitted Distribution', color='steelblue', figure = fig)
            relplot.plot_points(failures=(
              life_data['time'][life_data['censor'] != True]).to_list(),
                                func='SF',
                                label='failure data',
                                color='red',
                                alpha=0.7, figure = fig)
            plotted = True
          case 'km_plot':
            relnp.KaplanMeier(
              failures=(
                life_data['time'][life_data['censor'] != True]).to_list(),
              right_censored=(
                life_data['time'][life_data['censor'] == True]).to_list(),
              show_plot=True,
              print_results=False,
              plot_CI=True,
              CI=0.95,
              plot_type='SF',
              figure = fig
            )
            plotted = True
          # If an exact match is not confirmed, this last case will be used if provided
          case _:
            plotted = False
      except:
        plotted = False

      if plotted:
        plot_html = gff.helper_save_plot_as_html_image(fig = fig)
        plots[key] = {'title': key, 'img': plot_html}

  #adjust outputs if necessary
  if updates is not None:
    meta.update({"status":"Finalising outputs","current":3})
    self.update_state(state='PROGRESS', meta= meta)
    
  if (output == "html"):
    result = gff.helper_format_df_as_std_html(result)

  return {"Datatables": result, "Plots": plots}



def survival_analysis_celery(self,request_form,meta):
  #convert form request to input dictionary and then to dataframe
  meta.update({"status":"cleaning input data", "current":0,"total":3})
  self.update_state(state='PROGRESS', meta= meta)
  
  observed_life_data_dict = {
    'time': request_form['survivaltimes'],
    'censor': request_form['survivalcensor'],
    'qty': request_form['survivalqty']
  }
  observed_life_data_df = gff.helper_formdata_to_df(
    form_data=observed_life_data_dict)

  #manage checkboxes
  plot_options = {}
  for plotkey in ['probability_plot', 'sf_plot', 'km_plot']:
    if plotkey in request_form:
      plot_options[plotkey] = True
    else:
      plot_options[plotkey] = False

  #perform analysis
  analysis_results = survival_analysis(
    life_data=observed_life_data_df,
    grouped=True,
    output="html",
    method=request_form['fitmethod'],
    plot_options = plot_options,
    updates = [self,meta.copy()])

  return analysis_results