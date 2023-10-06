import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import app.static.helpers.global_formatting_functions as gff

BlockType = ["Equipment","System - Series", "System - Parallel"]

def new_rbd(SystemName = "System", SystemType = "System - Series", Description = "", M = None, N = None):
  d = {'Tag': SystemName,
      'Description': Description,
      'Level':1,
      'Type':SystemType,
      'M':M,
      'N':N}
  result = pd.DataFrame(data=d,  index=[1])
  return result



def add_rbd_block(RBD = new_rbd(), Tag = "", Description = "", Level = 2, Type = "Equipment", M = None, N = None):
  new_row = {'Tag': Tag,
      'Description': Description,
      'Level':Level,
      'Type':Type,
      'M':M,
      'N':N}
  
  RBD.loc[len(RBD)+1] = new_row
  
  result = RBD

  #system$Tag[nrow(system)] <- if_else(!is.None(Tag),Tag,paste0("Tag",nrow(system)+1))
  #system$Level[nrow(system)] <- if_else(!is.None(Level),Level,max(max(system$Level),2))
  
  return result



def rbd_examples():
  df = new_rbd("Firewater System")
  df = add_rbd_block(RBD = df, Tag = "Pump System", Level = 2, Type = "System - Parallel", M = 1, N = 2)
  df = add_rbd_block(RBD = df, Tag = "Pump Package 1", Level = 3, Type = "System - Series")
  df = add_rbd_block(RBD = df, Tag = "Pump 1", Level = 4, Type = "Equipment")
  df = add_rbd_block(RBD = df, Tag = "Motor 1", Level = 4, Type = "Equipment")
  df = add_rbd_block(RBD = df, Tag = "Pump Package 2", Level = 3, Type = "System - Series")
  df = add_rbd_block(RBD = df, Tag = "Pump 2", Level = 4, Type = "Equipment")
  df = add_rbd_block(RBD = df, Tag = "Motor 2", Level = 4, Type = "Equipment")
  df = add_rbd_block(RBD = df, Tag = "Pump Package 3", Level = 3, Type = "System - Series")
  df = add_rbd_block(RBD = df, Tag = "Pump 3", Level = 4, Type = "Equipment")
  df = add_rbd_block(RBD = df, Tag = "Motor 3", Level = 4, Type = "Equipment")
  df = add_rbd_block(RBD = df, Tag = "Ringmain", Level = 2, Type = "Equipment")
  df = add_rbd_block(RBD = df, Tag = "Nozzles", Level = 2, Type = "Equipment")
  firewater = df

  
  df = new_rbd("Basic Instrument Loop")
  df = add_rbd_block(RBD = df, Tag = "Sensor")
  df = add_rbd_block(RBD = df, Tag = "Controller")
  df = add_rbd_block(RBD = df, Tag = "Control Valve")
  instrument_loop = df


  df = new_rbd("Pumps in Parallel", SystemType = "System - Parallel", M = 2, N = 3)
  df = add_rbd_block(RBD = df, Tag = "Pump 1")
  df = add_rbd_block(RBD = df, Tag = "Pump 2")
  df = add_rbd_block(RBD = df, Tag = "Pump 3")
  pumps = df               
  
  result = {"compiled": {"firewater" : firewater,
                        "Instrument Loop" : instrument_loop,
                        "Pump System" : pumps},
           "deconstructed": {
             "firewater":{
               "meta":{
                 "title":"Firewater",
                 "desc":"Firewater system - pumps and spray sections"},
               "equipment":[
                 {"meta":{"tag":"Nozzles", "capacity":0}},
                 {"meta":{"tag":"Ringmain", "capacity":0}},
                 {"meta":{"tag":"Pump", "capacity":0}},
                 {"meta":{"tag":"Motor", "capacity":0}}
               ],
               "sub-systems":[
                 {"tag":"Pump Package",
                 "structure":[
                   {"tag":"Pump Package","type":"System - Series","level":1},
                   {"tag":"Pump","type":"Equipment","level":2,"localid":3},
                   {"tag":"Pump","type":"Equipment","level":2,"localid":4}
                 ]},
                 {"tag":"Pump System",
                 "structure":[
                   {"tag":"Pump System","type":"System - Parallel","level":1,"m":1,"n":2},
                   {"tag":"Pump Package","type":"Subsystem","level":2,"localid":1},
                   {"tag":"Pump Package","type":"Subsystem","level":2,"localid":1}
                 ]}
               ],
               "system":{}},
             "stabilisation": {
               "meta":{
                 "title":"condensate stabilisation system",
                 "desc":"5 train stabilisation system"},
               "equipment":[],
               "sub-systems":{},
               "system":{}}
           }}
  
  return(result)


def prepare_rbd(config_file = new_rbd()):
  result = {'blocks': None,
            'config': None,
            'size': None,
            'error': None}
  
  #Error checking
  
  if(list(config_file.columns)!=list(new_rbd().columns)):
    result["error"] = "structure issue with input file to RBD builder"
  elif(len(config_file) != sum(config_file.Level>0)):
    result["error"] = "Levels missing"
  elif(None in config_file.Type):
    result["error"] = "Block types need to be populated"

  #Construct index for plotting
  buffer = 0.75

  #Step 1. relate each child in the config file to it's parent
  config_file["id"] = config_file.index
  config_file["parent_id"] = config_file.apply(lambda x: 0  if(x["Level"] ==1) else max(config_file.id[(config_file.id < x["id"]) & (config_file.Level == (x["Level"]-1))]), axis = 1)

  
  #step 2. define the height and width for each block in the file. Equipment blocks are a fixed size
  # the size of system blocks depend on the number of children and on the block type. Parallel blocks
  config_file["Width"] = config_file.Type.apply(lambda x: 5 if (x=="Equipment") else 0)
  config_file["Height"] = config_file.Type.apply(lambda x: 2 if (x=="Equipment") else 0)

  for i in range(max(config_file.Level),0,-1):
    #data.loc[data['name'] == 'fred', 'A'] =
    config_file.loc[config_file.Level == i,'Width'] = config_file.apply(lambda x: 
                                                                  x["Width"] if (x["Width"] > 0) 
                                                                  else (
                                                                    ((sum(config_file.parent_id==x["id"])+1)*buffer+
                                                                     sum(config_file.Width[config_file.parent_id==x["id"]]))
                                                                    if x["Type"] == "System - Parallel"
                                                                    else (max(config_file.Width[config_file.parent_id==x["id"]])+2*buffer)), axis = 1)

    config_file.loc[config_file.Level == i,'Height'] = config_file.apply(lambda x: 
                                                                  x["Height"] if (x["Height"] > 0) 
                                                                  else (
                                                                    ((sum(config_file.parent_id==x["id"])+1)*buffer+
                                                                     sum(config_file.Height[config_file.parent_id==x["id"]]))
                                                                    if x["Type"] == "System - Series"
                                                                    else (max(config_file.Height[config_file.parent_id==x["id"]])+2*buffer)), axis = 1)
  
  #step 3 - add parent MooN indicator
  config_file.M.replace(to_replace = 'None', value = 0)
  config_file.N.replace('None',0)
  config_file["MooNChild"] = config_file.parent_id.apply(lambda x: False if x==0 else config_file.M[config_file.id == x]>0)

  
  #step 4 . position the origin of the blocks on the RBD
  config_file["x"] = config_file.apply(lambda x: x["Width"]/2+buffer if x["Level"] == 1 else 0, axis = 1)
  config_file["y"] = config_file.apply(lambda x: x["Height"]/2+buffer if x["Level"] == 1 else 0, axis = 1)

  
  for i in range(2,max(config_file.Level)+1):
    config_file.loc[config_file.Level == i,'x'] = config_file.apply(lambda x:
                                                              (sum(config_file.x[config_file.id == x["parent_id"]]) -
                                                              sum(config_file.Width[config_file.id == x["parent_id"]])/2 +
                                                              sum(config_file.Width[(config_file.parent_id == x["parent_id"]) &
                                                                  (config_file.id < x["id"])]) +
                                                              (sum((config_file.parent_id == x["parent_id"]) &
                                                                  (config_file.id < x["id"]))+1)*buffer +
                                                              x["Width"]/2) 
                                                              if any(config_file.Type[config_file.id == x["parent_id"]]=="System - Parallel")
                                                              else sum(config_file.x[config_file.id == x["parent_id"]]),axis = 1)
    config_file.loc[config_file.Level == i,'y'] = config_file.apply(lambda x:
                                                              (sum(config_file.y[config_file.id == x["parent_id"]]) -
                                                              sum(config_file.Height[config_file.id == x["parent_id"]])/2 +
                                                              sum(config_file.Height[(config_file.parent_id == x["parent_id"]) &
                                                                  (config_file.id < x["id"])]) +
                                                              (sum((config_file.parent_id == x["parent_id"]) &
                                                                  (config_file.id < x["id"]))+1)*buffer +
                                                              x["Height"]/2) 
                                                              if any(config_file.Type[config_file.id == x["parent_id"]]=="System - Series")
                                                              else sum(config_file.y[config_file.id == x["parent_id"]]),axis = 1)
  

  #set up range of styles
  
  #draw blocks
  config_file["x1"] = config_file.apply(lambda x: x["x"] - x["Width"]/2, axis = 1)
  config_file["x2"] = config_file.apply(lambda x: x["x"] + x["Width"]/2, axis = 1)
  config_file["y1"] = config_file.apply(lambda x: x["y"] - x["Height"]/2, axis = 1)
  config_file["y2"] = config_file.apply(lambda x: x["y"] + x["Height"]/2, axis = 1)

  #
  config_file["conn"] = config_file.apply(lambda x:
                                         None if x["parent_id"]==0
                                         else 
                                          (None if (x["id"] == max(config_file.id[config_file.parent_id == x["parent_id"]])) 
                                           else
                                           ("parallel" if any(config_file.Type[config_file.id == x["parent_id"]]=="System - Parallel") else "series")), axis=1)
  config_file["conn_to"] = config_file.apply(lambda x: None if x["conn"] is None else min(config_file.id[(config_file.parent_id == x["parent_id"]) & (config_file.id > x["id"])]), axis=1)

  result["config"] = config_file
  result["size"] = {'x':config_file.x2[1]+buffer,
                   'y':config_file.y2[1]+buffer}
  
  return(result)


def draw_rbd_image(rbd_size, rbd_config):
  #define Matplotlib figure and axis
  fig, ax = plt.subplots()
  
  #plot blocks
  for block_index in rbd_config.index:
    ax.add_patch(Rectangle((rbd_config.x[block_index]-rbd_config.Width[block_index]/2, rbd_config.y[block_index]-rbd_config.Height[block_index]/2), rbd_config.Width[block_index], rbd_config.Height[block_index], edgecolor = 'black'))
    ax.text(rbd_config.x[block_index], rbd_config.y[block_index]+rbd_config.Height[block_index]/2-0.5, rbd_config.Tag[block_index], fontsize=6, horizontalalignment='center')

  #plot lines
    if (rbd_config.conn[block_index]=="series"):
      x1 = rbd_config.x[block_index] # middle of current block
      x2 = x1 # middle of 'to' block
      y1 = rbd_config.y2[block_index] # top of current block
      y2 = rbd_config.loc[rbd_config.id == rbd_config.conn_to[block_index], 'y1'].values[0] # middle of 'to' block
      ax.plot([x1, x2],[y1, y2],color='black')
    elif(rbd_config.conn[block_index]=="parallel"):
      x1 = rbd_config.x[block_index] # middle of current block
      x2 = rbd_config.x[rbd_config.id == rbd_config.conn_to[block_index]].values[0] # middle of 'to' block
      y1 = rbd_config.y2[block_index]+0.25 # top of current block
      y1a = rbd_config.y2[block_index]
      y2 = rbd_config.y1[block_index]-0.25 # middle of 'to' block
      y2a = rbd_config.y1[block_index]
      ax.plot([x1, x2],[y1, y1],color='black')
      ax.plot([x1, x1],[y1a, y1],color='black')
      ax.plot([x2, x2],[y1a, y1],color='black')
      ax.plot([x1, x2],[y2, y2],color='black')
      ax.plot([x1, x1],[y2a, y2],color='black')
      ax.plot([x2, x2],[y2a, y2],color='black')
      



  #adjust axes
  plt.xlim(0, rbd_size["x"])
  plt.ylim(0, rbd_size["y"])
  plt.axis('off')
  
  #display plot
  #plt.show()

  rbd_png = gff.helper_save_curr_plt_as_byte()
  
  return rbd_png