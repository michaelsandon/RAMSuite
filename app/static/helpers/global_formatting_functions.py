import pandas as pd
from json import loads
from bs4 import BeautifulSoup
from io import BytesIO
import base64
import matplotlib.pyplot as plt


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


def helper_format_df_as_std_html(df):
  html_table = df.to_html(justify='left')
  html_table = helper_add_class_to_tags(base_html=html_table,
                                        mods=[{
                                          'tag': "table",
                                          'class': "table"
                                        }, {
                                          'tag': "thead",
                                          'class': "table-dark"
                                        }])
  return html_table


def helper_save_curr_plt_as_byte():
  figfile = BytesIO()
  plt.savefig(figfile, format='png')
  figfile.seek(0)
  figure_png = base64.b64encode(figfile.getvalue()).decode('ascii')
  plt.clf()

  return figure_png


def helper_format_request(var):
  var2 = {}
  for key in var.keys():
    if len(var[key]) > 0:
      try:
        var2[key] = int(var[key])
      except:
        try:
          var2[key] = float(var[key])
        except:
          var2[key] = var[key]
    else:
      var2[key] = None
  return var2
