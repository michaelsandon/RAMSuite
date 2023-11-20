import pandas as pd
from json import loads
from bs4 import BeautifulSoup
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import markdown
from flask import url_for


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

def helper_dict_to_std_html(dict, name = None):
  frame = pd.Series(dict, name = name).to_frame()
  result = helper_format_df_as_std_html(frame)
  return result


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



def helper_format_df_as_std_html(df, ff = None, formatters = None, table_id = None):
  #'{:,.2%}'.format
  
  html_table = df.to_html(justify='left', render_links=True, escape=False, float_format = ff, formatters = formatters, table_id=table_id)
  html_table = helper_add_class_to_tags(base_html=html_table,
                                        mods=[{
                                          'tag': "table",
                                          'class': "table"
                                        }, {
                                          'tag': "thead",
                                          'class': "table-dark"
                                        }])
  return html_table

def helper_format_parent_child_dfs_as_html(dfparent,dfchild,parentidcol="id", childparentidcol = "parentid"):
  dfparent["descriptor"] = dfparent.apply(lambda x: '--'.join('{}: {}'.format(key, value) for key, value in x.to_dict().items()), axis=1)
  
  for i in range(len(dfparent)):
    subsetdf = dfchild[dfchild[childparentidcol] == dfparent[parentidcol][i]]
    subsethtml = subsetdf.to_html(justify="left", index=False)
    
    if i == 0:
      soup = BeautifulSoup(subsethtml, 'html.parser')
      
    new_td = soup.new_tag("td")
    new_tr = soup.new_tag("tr")
    new_td["colspan"] = len(dfchild.columns)
    new_td.string = dfparent["descriptor"][i]
    new_tr.append(new_td)

    if i == 0:
      soup.tbody.insert(0,new_tr)
    else:
      soup.tbody.append(new_tr)
      soup2 = BeautifulSoup(subsethtml, 'html.parser')
      soup.tbody.append(BeautifulSoup(soup2.tbody.encode_contents(), 'html.parser'))

  
  html_table = helper_add_class_to_tags(base_html=str(soup),
                                      mods=[{
                                        'tag': "table",
                                        'class': "table"
                                      }, {
                                        'tag': "thead",
                                        'class': "table-dark"
                                      }])
  return html_table



def helper_read_and_format_markdown(mkdwnfile):
  
  with open(mkdwnfile) as mdfile:
    mkdwn = markdown.markdown(mdfile.read(), extensions=['extra','sane_lists'])
    mkdwn = helper_add_class_to_tags(base_html = mkdwn, mods=[{'tag': "table", 'class': "table"},{'tag': "thead", 'class': "table-dark"}])

  return mkdwn

#def test(df):
#  df["newcol"] = df.apply(lambda x: '--'.join('{}: {}'.format(key, value) #for key, value in x.to_dict().items()), axis=1)
#  return df
  

def helper_save_curr_plt_as_byte(axes_handle = None, fig = None):
  #https://www.geeksforgeeks.org/matplotlib-axes-axes-get_figure-in-python/ update this function
  figfile = BytesIO()
  if (axes_handle is None) & (fig is None):
    plt.savefig(figfile, format='png',bbox_inches='tight')
    plt.clf()
    plt.close()
  else:
    if fig is None:
      fig = axes_handle.get_figure()   
    fig.savefig(figfile, format='png',bbox_inches='tight')
    fig.clear()
    plt.close(fig)

  figfile.seek(0)
  figure_png = base64.b64encode(figfile.getvalue()).decode('ascii')
  plt.clf()

  return figure_png

def helper_save_byte_as_image_tag(bytefile,plot_width = 500):
  result = '<img src="data:image/png;base64,'+bytefile+'" width="'+str(plot_width)+'">'
  return result

def helper_save_plot_as_html_image(axes_handle = None, fig = None, plot_width = 500):
  encoded_plot = helper_save_curr_plt_as_byte(axes_handle = axes_handle, fig = fig)
  html_image = helper_save_byte_as_image_tag(bytefile = encoded_plot,plot_width = plot_width)
  return html_image

#Especially when you are running multiple processes or threads, it is much better to define your figure variable and work with it directly:

#from matplotlib import pyplot as plt

#f = plt.figure()
#f.clear()
#plt.close(f)


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



def helper_add_links_to_frame_as_html(task_id, df = None, n_sims = None, table_id=None):
  if df is None:
    df = pd.DataFrame({"Sim Id":range(1,n_sims+1)})

  df["link"] = df.apply(lambda x: "<a href="+ url_for('availability.ram_sim_result', task_id = task_id, sim_id = x["Sim Id"]) + ">link</a>", axis=1)
  result = helper_format_df_as_std_html(df, table_id = table_id)

  return result



  

  