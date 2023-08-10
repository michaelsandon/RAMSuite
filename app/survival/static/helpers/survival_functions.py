import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import reliability.Fitters as relfit
import reliability.Probability_plotting as relplot
import reliability.Nonparametric as relnp
import pandas as pd
from json import loads
from io import BytesIO
import base64


def helper_formdata_to_df(form_data: dict):
  result = {}
  for key in list(form_data.keys()):
    result[key] = loads(form_data[key])
  return pd.DataFrame(data=result)


def series_to_html(pd_series):
  frame = pd.Series.to_frame(pd_series)
  return frame.to_html()


def survival_analysis(life_data,
                      grouped=False,
                      output="html",
                      method="Weibull_2P",
                      plot_options={'probability_plot':True, 'sf_plot':True, 'mle_plot':True}):

  #clean up df if needed
  life_data = life_data.fillna(value={'qty': 1, 'censor': False})
  life_data = life_data[life_data['time'].notnull()]

  #transform life data if needed from grouped to single obs
  if (grouped):
    life_data = pd.DataFrame(life_data.values.repeat(life_data.qty, axis=0),
                             columns=life_data.columns).drop('qty', axis=1)

  #perform analysis
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
  plots = {}

  for key, plotitem in plot_options.items():
    figfile = BytesIO()
    if plotitem:
      plotted = False     
      match key:
        case 'probability_plot':
          fit_func(
            failures=(life_data['time'][life_data['censor'] != True]).to_list(),
            right_censored=(life_data['time'][life_data['censor'] == True]).to_list(),
            show_probability_plot=True,
            print_results=False,
            downsample_scatterplot=False)
          plotted = True
        case 'sf_plot':
          fit.distribution.SF(label='Fitted Distribution', color='steelblue')
          relplot.plot_points(
            failures=(life_data['time'][life_data['censor'] != True]).to_list(),
            func='SF',
            label='failure data',
            color='red',
            alpha=0.7)
          plotted = True
        case 'mle_plot':
          plotted = False
        # If an exact match is not confirmed, this last case will be used if provided
        case _:
          plotted = False
          
      if plotted:
        plt.savefig(figfile, format='png')
        figfile.seek(0)
        plot_png = base64.b64encode(figfile.getvalue()).decode('ascii')        
        plots[key] = {
          'title': key,
          'img': plot_png
        }
        plt.clf()


  #adjust outputs if necessary
  if (output == "html"):
    result = result.to_html(
      classes=["thead-dark", "table", "table-responsive"])

  return {"Datatables": result, "Plots": plots}
