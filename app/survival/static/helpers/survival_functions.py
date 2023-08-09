import matplotlib
matplotlib.use('agg')
import weibull as wb
import reliability.Fitters as relfit
import pandas as pd
from json import loads


def helper_formdata_to_df(form_data: dict):
  result = {}
  for key in list(form_data.keys()):
    result[key] = loads(form_data[key])
  return pd.DataFrame(data=result)


def fit_weibull(fail_times=[10, 11, 9, 8, 10, 11]):
  analysis = weibull.Analysis(fail_times, unit='hour')
  analysis.fit(method='mle', confidence_level=0.9)
  return analysis.stats


def series_to_html(pd_series):
  frame = pd.Series.to_frame(pd_series)
  return frame.to_html()


def survival_analysis(life_data,
                      grouped=False,
                      output="html",
                      method="Weibull_2P"):

  #clean up df if needed
  life_data = life_data.fillna(value={'qty': 1, 'censor': False})
  life_data = life_data[life_data['time'].notnull()]

  #transform life data if needed from grouped to single obs
  if (grouped):
    life_data = pd.DataFrame(life_data.values.repeat(life_data.qty, axis=0),
                             columns=life_data.columns).drop('qty', axis=1)

  #perform analysis
  print(life_data)
  fit_func = getattr(relfit, "Fit_" + method)
  fit = fit_func(
    failures=(life_data['time'][life_data['censor'] != True]).to_list(),
    right_censored=(life_data['time'][life_data['censor'] == True]).to_list(),
    show_probability_plot=True,
    print_results=False,
    downsample_scatterplot=False)

  result = fit.results

  #adjust outputs if necessary
  if (output == "html"):
    result = result.to_html()

  return result
