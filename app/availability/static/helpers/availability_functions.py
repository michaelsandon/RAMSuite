import reliability.Distributions as reldist
import pandas as pd
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from functools import reduce
import app.static.helpers.global_formatting_functions as gff
import app.static.helpers.global_reliability_helpers as grh

def helper_sample_from_dist(dist_as_dict, n_samples=1):

  if dist_as_dict['dist'] in ['constant','const','Constant','Const']:
    samples = [dist_as_dict['par1']] * n_samples
  else:
    #acquire dist
    dist_func = getattr(reldist, dist_as_dict['dist'])
    try:
      dist = dist_func(dist_as_dict['par1'], dist_as_dict['par2'],
                       dist_as_dict['par3'])
    except:
      try:
        dist = dist_func(dist_as_dict['par1'], dist_as_dict['par2'])
      except:
        dist = dist_func(dist_as_dict['par1'])

    #get samples
    samples = dist.random_samples(n_samples).tolist()

  return samples




def _equipment_uptime(tbe={
  'dist': "Weibull_Distribution",
  'par1': 20,
  'par2': 2,
  'par3': None
},
                      dt={
                        'dist': "constant",
                        'par1': 10,
                        'par2': None,
                        'par3': None
                      },
                      dur=100,
                      sim_id=None):

  #set state
  state = [1]  #ready to start
  t = [0]

  while t[-1] < dur:
    if state[-1] == 1:
      #sample a life
      new_life = helper_sample_from_dist(dist_as_dict=tbe)[-1]
      t.append(t[-1] + new_life)
      state.append(1)
      t.append(t[-1])
      state.append(0)
    else:
      repair_time = helper_sample_from_dist(dist_as_dict=dt)[-1]
      t.append(t[-1] + repair_time)
      state.append(0)
      t.append(t[-1])
      state.append(1)

  #create time series of life
  state_df = pd.DataFrame({'time': t, 'state': state})

  if sim_id != None:
    state_df['simulation'] = sim_id

  #state_df.set_index('time', inplace=True)

  return state_df




#need to refactor this code NOT in USE
def package_uptime_pool(tbe={
  'dist': "Weibull_Distribution",
  'par1': 20,
  'par2': 2,
  'par3': None
},
                        dt={
                          'dist': "constant",
                          'par1': 10,
                          'par2': None,
                          'par3': None
                        },
                        n_parallel=1,
                        n_req=None,
                        dur=100,
                        n_sims=10):
  #initialise return objects
  result_list = []

  #use pool
  with Pool(processes=4, initializer=grh.helper_init_seed) as pool:
    all_sims = [
      pool.apply_async(_package_uptime, [tbe, dt, dur, id])
      for id in range(n_sims)
    ]

    for i in all_sims:
      df = i.get(timeout=None)
      result_list.append(df)

  result = pd.concat(result_list)

  return result


def _package_uptime_thread(tbe={
  'dist': "Weibull_Distribution",
  'par1': 20,
  'par2': 2,
  'par3': None
},
                           dt={
                             'dist': "constant",
                             'par1': 10,
                             'par2': None,
                             'par3': None
                           },
                           n_parallel=1,
                           n_req=None,
                           dur=100,
                           sim_id=None):
  #initialise return objects
  result_list = []

  #use nested threads
  if n_parallel == 1:
    result = _equipment_uptime(tbe=tbe, dt=dt, dur=dur, sim_id=sim_id)
  else:
    with ThreadPool(n_parallel, initializer=grh.helper_init_seed) as pool:
      all_sims = [
        pool.apply_async(_equipment_uptime, [tbe, dt, dur])
        for id in range(n_parallel)
      ]

      counter = 1
      for i in all_sims:
        df = i.get(timeout=None)
        df.set_index('time', inplace=True)
        result_list.append(df.squeeze().rename("Eq" + str(counter)))
        counter = counter + 1

      # close the pool
      pool.close()
      # wait for all tasks to be processed
      pool.join()

    #combine package
    result = reduce(
      lambda df1, df2: pd.merge(
        df1, df2, right_index=True, left_index=True, how='outer'),
      result_list).interpolate()
    result['state'] = result.apply(lambda x: 1 if sum(x) >=
                                   (n_parallel
                                    if n_req == None else n_req) else 0,
                                   axis=1)
    result = pd.DataFrame({'time': result.index, 'state': result['state']})
    result.reset_index(inplace=True, drop=True)
    if sim_id != None:
      result['simulation'] = sim_id

  return result


def package_uptime_thread(tbe={
  'dist': "Weibull_Distribution",
  'par1': 20,
  'par2': 2,
  'par3': None
},
                          dt={
                            'dist': "constant",
                            'par1': 10,
                            'par2': None,
                            'par3': None
                          },
                          n_parallel=1,
                          n_req=None,
                          dur=100,
                          n_sims=10):
  #initialise return objects
  result_list = []

  #use pool
  with Pool(processes=2, initializer=grh.helper_init_seed) as pool:
    #with ThreadPool(10, initializer=helper_init_seed) as pool:
    all_sims = [
      pool.apply_async(_package_uptime_thread,
                       [tbe, dt, n_parallel, n_req, dur, id])
      for id in range(n_sims)
    ]

    for i in all_sims:
      df = i.get(timeout=None)
      result_list.append(df)

  result = pd.concat(result_list)

  return result


def _package_uptime_long(tbe={
  'dist': "Weibull_Distribution",
  'par1': 20,
  'par2': 2,
  'par3': None
},
                           dt={
                             'dist': "constant",
                             'par1': 10,
                             'par2': None,
                             'par3': None
                           },
                           n_parallel=1,
                           n_req=None,
                           dur=100,
                           sim_id=None):
  #initialise return objects
  result_list = []

  #use nested threads
  if n_parallel == 1:
    result = _equipment_uptime(tbe=tbe, dt=dt, dur=dur, sim_id=sim_id)
  else:
    #run sims at equipment level
    counter = 1
    for id in range(n_parallel):
      df = _equipment_uptime(tbe, dt, dur)
      df.set_index('time', inplace=True)
      result_list.append(df.squeeze().rename("Eq" + str(counter)))
      counter = counter + 1

    #combine package
    result = reduce(
      lambda df1, df2: pd.merge(
        df1, df2, right_index=True, left_index=True, how='outer'),
      result_list).interpolate()
    result['state'] = result.apply(lambda x: 1 if sum(x) >=
                                   (n_parallel
                                    if n_req == None else n_req) else 0,
                                   axis=1)
    result = pd.DataFrame({'time': result.index, 'state': result['state']})
    result.reset_index(inplace=True, drop=True)
    if sim_id != None:
      result['simulation'] = sim_id

  return result


def package_uptime_long(tbe={
  'dist': "Weibull_Distribution",
  'par1': 20,
  'par2': 2,
  'par3': None
},
                          dt={
                            'dist': "constant",
                            'par1': 10,
                            'par2': None,
                            'par3': None
                          },
                          n_parallel=1,
                          n_req=None,
                          dur=100,
                          n_sims=10,
                          updates = None):
  #initialise return objects
  result_list = []

  #use pool
  for id in range(n_sims):
    df = _package_uptime_long(tbe,dt,n_parallel,n_req,dur,id)
    result_list.append(df)
    if updates != None:
      task_obj = updates[0]
      meta = updates[1]
      meta["current"]=id+1
      task_obj.update_state(state = "PROGRESS",meta=meta)

  result = pd.concat(result_list)

  return result
  

def _uptime_statistics(uptime_signal):
  #expect input as a datafrae with only two columns: time, state
  calc_df = uptime_signal
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
  calc_df['cap_uptime'] = (calc_df['time'] - calc_df['lag_time']) * (
    (calc_df['state'] + calc_df['lag_state']) / 2)

  #fill any NaN generated from shifts
  calc_df = calc_df.fillna(0)

  #results
  result = {}
  result['dt_events'] = calc_df['downtime_ind'].sum()
  result['uptime'] = calc_df['uptime'].sum()
  result['Ao'] = calc_df['uptime'].sum() / (calc_df['time'].max() -
                                            calc_df['time'].min())
  result['Ao_cap'] = calc_df['cap_uptime'].sum() / (calc_df['time'].max() -
                                                    calc_df['time'].min())

  return result


def uptime_statistics_pool(uptime_signals):
  if 'simulation' in uptime_signals.columns:
    result_list = []
    stats_list = []

    with Pool(processes=4) as pool:

      for i in uptime_signals.simulation.unique():
        uptime_signal = uptime_signals[uptime_signals['simulation'] == i]
        stat = pool.apply_async(_uptime_statistics, [uptime_signal])
        stats_list.append(stat)

      for i in stats_list:
        stat = i.get(timeout=None)
        result_list.append(pd.DataFrame([stat]))

    result = pd.concat(result_list)

  else:
    result = pd.DataFrame(_uptime_statistics(uptime_signals))

  return result


def _uptime_statistics_long(uptime_signal):
  #expect input as a datafrae with only two columns: time, state
  calc_df = uptime_signal
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
  calc_df['cap_uptime'] = (calc_df['time'] - calc_df['lag_time']) * (
    (calc_df['state'] + calc_df['lag_state']) / 2)

  #fill any NaN generated from shifts
  calc_df = calc_df.fillna(0)

  #results
  result = {}
  result['dt_events'] = calc_df['downtime_ind'].sum()
  result['uptime'] = calc_df['uptime'].sum()
  result['Ao'] = calc_df['uptime'].sum() / (calc_df['time'].max() -
                                            calc_df['time'].min())
  result['Ao_cap'] = calc_df['cap_uptime'].sum() / (calc_df['time'].max() -
                                                    calc_df['time'].min())

  return result



def uptime_statistics_long(uptime_signals, updates = None):
  if 'simulation' in uptime_signals.columns:
    result_list = []

    counter = 0
    for i in uptime_signals.simulation.unique():
      counter = counter +1
      uptime_signal = uptime_signals[uptime_signals['simulation'] == i]
      stat = _uptime_statistics_long(uptime_signal)
      result_list.append(pd.DataFrame([stat]))
      if updates != None:
        task_obj = updates[0]
        meta = updates[1]
        meta["current"]=counter
        task_obj.update_state(state = "PROGRESS",meta=meta)

    result = pd.concat(result_list)

  else:
    result = pd.DataFrame(_uptime_statistics_long(uptime_signals))

  return result




  
def package_uptime_parallel_process(self, request_form):
  result = {}

  request_data = gff.helper_format_request(request_form)#request.form)

  #organise request data into inputs
  tbe = {
    'dist': request_data['ev_dist'],
    'par1': request_data['ev_param1'],
    'par2': request_data['ev_param2'],
    'par3': request_data['ev_param3']
  }

  dt = {
    'dist': request_data['dt_dist'],
    'par1': request_data['dt_param1'],
    'par2': request_data['dt_param2'],
    'par3': request_data['dt_param3']
  }

  self.update_state(state='PROGRESS',
                    meta={
                      'current': 0,
                      'total': request_data['n_sims'],
                      'status': "Running Simulations"
                    })

  simulation_ts = package_uptime_thread(tbe=tbe,
                                        dt=dt,
                                        n_parallel=request_data['n_parallel'],
                                        n_req=request_data['n_req'],
                                        dur=request_data['dur'],
                                        n_sims=request_data['n_sims'])
  
  
  self.update_state(state='PROGRESS',
                    meta={
                      'current': 0,
                      'total': request_data['n_sims'],
                      'status': "Preparing Results"
                    })
  
  simulation_stats = uptime_statistics_pool(simulation_ts)

  result['ts'] = gff.helper_format_df_as_std_html(simulation_ts)
  result['stats'] = gff.helper_format_df_as_std_html(simulation_stats)

  return result




def package_uptime_celery(self, request_form, meta):
  result = {}

  request_data = gff.helper_format_request(request_form)#request.form)

  #organise request data into inputs
  tbe = {
    'dist': request_data['ev_dist'],
    'par1': request_data['ev_param1'],
    'par2': request_data['ev_param2'],
    'par3': request_data['ev_param3']
  }

  dt = {
    'dist': request_data['dt_dist'],
    'par1': request_data['dt_param1'],
    'par2': request_data['dt_param2'],
    'par3': request_data['dt_param3']
  }

  meta['total'] = request_data['n_sims']
  meta['status'] = "Running Simulations"
  
  self.update_state(state='PROGRESS', meta=meta)

  simulation_ts = package_uptime_long(tbe=tbe,
                                      dt=dt,
                                      n_parallel=request_data['n_parallel'],
                                      n_req=request_data['n_req'],
                                      dur=request_data['dur'],
                                      n_sims=request_data['n_sims'],
                                      updates = [self,meta.copy()])
  

  
  meta['status'] = "Processing Results"
  self.update_state(state='PROGRESS', meta= meta)
  
  simulation_stats = uptime_statistics_long(simulation_ts, updates = [self,meta.copy()])


  meta['status'] = "Formatting Results"
  meta["total"] = 2
  self.update_state(state='PROGRESS', meta= meta)
  
  result['ts'] = gff.helper_format_df_as_std_html(simulation_ts.head(100))
  simulation_ts.reset_index(inplace=True)
  result['ts_df'] = simulation_ts.to_json()

  meta["current"] = 1
  self.update_state(state='PROGRESS', meta= meta)
  
  result['stats'] = gff.helper_format_df_as_std_html(simulation_stats)

  return result