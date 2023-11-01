from numpy.random import seed
import pandas as pd
import matplotlib.pyplot as plt
import app.static.helpers.global_formatting_functions as gff


def helper_init_seed():
  seed()

def process_uptime_signals(signaldf, signaltype = None,sim_id = None):
  #expect input as a dataframe with multiple columns: time, fm1,fm2
  columns = ['signalid','dt_events','uptime','uptime_%','mwa_sig_val']
  result = pd.DataFrame(columns=columns)

  signals = signaldf.columns.to_list()
  signals.remove("Time")
  signaldf.rename(columns={"Time":"time"}, inplace=True)
  signaldf['lag_time'] = signaldf['time'].shift(1)
  
  for sigid in signals:
    calc_df = signaldf.loc[:,["time","lag_time",sigid]].rename(columns={sigid:"state"})
    calc_df['lag_state'] = calc_df['state'].shift(1)
    #define event indicator
    calc_df['downtime_ind'] = calc_df.apply(
      lambda x: 1 if x['state'] != x['lag_state'] and x['state'] == 0 else 0,
      axis=1)
  
    #define uptime
    calc_df['lag_time'] = calc_df['time'].shift(1)
    calc_df['uptime'] = calc_df.apply(
      lambda x: x['time'] - x['lag_time']
      if x['state'] == 1 and x['lag_state'] == 1 else 0,
      axis=1)
  
    #define capacity based uptime
    calc_df['tw_val'] = (calc_df['time'] - calc_df['lag_time']) * (
      (calc_df['state'] + calc_df['lag_state']) / 2)
  
    #fill any NaN generated from shifts
    calc_df = calc_df.fillna(0)
  
    #results
    result.loc[len(result)] = {'signalid':sigid,
                               'dt_events':calc_df['downtime_ind'].sum(),
                               'uptime':calc_df['uptime'].sum(),
                               'uptime_%':calc_df['uptime'].sum() / (calc_df['time'].max() - calc_df['time'].min()),
                               'mwa_sig_val':calc_df['tw_val'].sum() / (calc_df['time'].max() - calc_df['time'].min())}


  if sim_id is not None:
    result["sim_id"] = sim_id

  if signaltype == "eq":
    result.rename(columns={"mwa_sig_val":"mean-weighted-average-availability"}, inplace=True)
  if signaltype == "matl":
    result.rename(columns={"dt_events":"stock-out_events","mwa_sig_val":"avg-stock-in-inventory","signalid":"matl"}, inplace=True)
    result.drop(columns=["uptime","uptime_%"], inplace=True)
      
  return result



def helper_plot_time_based_df_as_html_image(signaldf, plottype = "line", subplottitle = "Subplot {var}"):
  signals = signaldf.columns.to_list()
  signals.remove("Time")
  num_plots = len(signals)
  fig, axs = plt.subplots(num_plots,figsize=(9,3*num_plots))
  for i in range(num_plots):
    if plottype == "line":
      axs[i].plot(signaldf.loc[:,"Time"],signaldf.loc[:,signals[i]])
    elif plottype == "area":
      axs[i].fillbetween(x = signaldf.loc[:,"Time"], y1 = signaldf.loc[:,signals[i]])
    axs[i].set_title(subplottitle.format(var = signals[i]))

  plt.subplots_adjust(hspace=0.4)
  fig = gff.helper_save_curr_plt_as_byte()
  result = gff.helper_save_byte_as_image_tag(fig)
  return result