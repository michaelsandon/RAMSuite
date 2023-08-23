import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt
import reliability.Distributions as reldist
import reliability.Fitters as relfit
import reliability.Probability_plotting as relplot
import reliability.Nonparametric as relnp
import reliability.Other_functions as reloth
import pandas as pd
from json import loads
from io import BytesIO
import base64
from bs4 import BeautifulSoup


def helper_formdata_to_df(form_data: dict):
  result = {}
  for key in list(form_data.keys()):
    result[key] = loads(form_data[key])
  return pd.DataFrame(data=result)


def helper_formdata_to_list(form_data: dict):
  result = {}
  for key in list(form_data.keys()):
    if (len(form_data[key]) > 0):
      result[key] = loads(form_data[key])
    else:
      result[key] = None
  return list(result.values())


def helper_series_to_html(pd_series):
  frame = pd.Series.to_frame(pd_series)
  return frame.to_html()


def helper_add_class_to_tags(base_html, mods=[{'tag': "", 'class': ""}]):
  #read in html
  soup = BeautifulSoup(base_html, 'html.parser')

  for mod in mods:
    if (mod['tag'] != ""):
      target_tags = soup.find_all(mod['tag'])
      for tag in target_tags:
        try:
          tag['class'].append(mod["class"])
        except:
          tag['class'] = mod["class"]

  #convert tree back to string
  return (str(soup))


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
    sampleresult = samples_df.to_html(justify='left')
    sampleresult = helper_add_class_to_tags(base_html=sampleresult,
                                            mods=[{
                                              'tag': "table",
                                              'class': "table"
                                            }, {
                                              'tag': "thead",
                                              'class': "table-dark"
                                            }])
  else:
    sampleresult = samples_df

  #histogram
  plot_png = None
  if histogram:
    figfile = BytesIO()
    reloth.histogram(samples)
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    plot_png = base64.b64encode(figfile.getvalue()).decode('ascii')
    plt.clf()

  return {'samples': sampleresult, 'histogram': plot_png}


def survival_analysis(life_data,
                      grouped=False,
                      output="html",
                      method="Weibull_2P",
                      plot_options={
                        'probability_plot': True,
                        'sf_plot': True,
                        'km_plot': True
                      }):

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
              downsample_scatterplot=False)
            plotted = True
          case 'sf_plot':
            fit.distribution.SF(label='Fitted Distribution', color='steelblue')
            relplot.plot_points(failures=(
              life_data['time'][life_data['censor'] != True]).to_list(),
                                func='SF',
                                label='failure data',
                                color='red',
                                alpha=0.7)
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
              plot_type='SF')
            plotted = True
          # If an exact match is not confirmed, this last case will be used if provided
          case _:
            plotted = False
      except:
        plotted = False

      if plotted:
        plt.savefig(figfile, format='png')
        figfile.seek(0)
        plot_png = base64.b64encode(figfile.getvalue()).decode('ascii')
        plots[key] = {'title': key, 'img': plot_png}
        plt.clf()

  #adjust outputs if necessary
  if (output == "html"):
    result = result.to_html(index=False, justify="left")
    result = helper_add_class_to_tags(base_html=result,
                                      mods=[{
                                        'tag': "table",
                                        'class': "table"
                                      }, {
                                        'tag': "thead",
                                        'class': "table-dark"
                                      }])

  return {"Datatables": result, "Plots": plots}
