import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import app.static.helpers.global_formatting_functions as gff

Blocktype = ["Equipment","System - Series", "System - Parallel"]




#function for compiling ram model
def compile_ram_system(equipmentdf, subsystemdf, systemdf):
  #clean up cols
  
  compiled_system = systemdf
  print("Subsystem" in compiled_system["type"])
  while any(compiled_system["type"] == "Subsystem"):
    target_node = min(compiled_system.id[compiled_system.type=="Subsystem"])
    print(target_node)
    topdf = compiled_system[compiled_system.id < target_node]
    bottomdf = compiled_system[compiled_system.id > target_node]
    insertdf = subsystemdf[subsystemdf.subsystemid == compiled_system.refid.loc[compiled_system.id == target_node].values[0]]
    insertdf["level"] = insertdf.level+compiled_system.level.loc[compiled_system.id == target_node].values[0]-1
    insertdf.drop(['subsystemid'], axis=1)
    compiled_system = pd.concat([topdf,insertdf,bottomdf])
    compiled_system.reset_index(drop=True,inplace=True)
    compiled_system.id = compiled_system.index+1

  return compiled_system
  
#function to prepare an RBD for plotting given a compiled RBD system
def prepare_rbd(config_file = new_rbd()):
  result = {'blocks': None,
            'config': None,
            'size': None,
            'error': None}
  
  #Error checking
  
  if(list(config_file.columns)!=list(new_rbd().columns)):
    result["error"] = "structure issue with input file to RBD builder"
  elif(len(config_file) != sum(config_file.level>0)):
    result["error"] = "levels missing"
  elif(None in config_file.type):
    result["error"] = "Block types need to be populated"

  #Construct index for plotting
  buffer = 0.75

  #Step 1. relate each child in the config file to it's parent
  if "id" not in config_file.columns:
    config_file.reset_index(inplace=True,drop=True)
    config_file["id"] = config_file.index
    
  config_file["parent_id"] = config_file.apply(lambda x: 0  if(x["level"] ==1) else max(config_file.id[(config_file.id < x["id"]) & (config_file.level == (x["level"]-1))]), axis = 1)

  
  #step 2. define the height and width for each block in the file. Equipment blocks are a fixed size
  # the size of system blocks depend on the number of children and on the block type. Parallel blocks
  config_file["Width"] = config_file.type.apply(lambda x: 5 if (x=="Equipment") else 0)
  config_file["Height"] = config_file.type.apply(lambda x: 2 if (x=="Equipment") else 0)

  for i in range(max(config_file.level),0,-1):
    #data.loc[data['name'] == 'fred', 'A'] =
    config_file.loc[config_file.level == i,'Width'] = config_file.apply(lambda x: 
                                                                  x["Width"] if (x["Width"] > 0) 
                                                                  else (
                                                                    ((sum(config_file.parent_id==x["id"])+1)*buffer+
                                                                     sum(config_file.Width[config_file.parent_id==x["id"]]))
                                                                    if x["type"] == "System - Parallel"
                                                                    else (max(config_file.Width[config_file.parent_id==x["id"]])+2*buffer)), axis = 1)

    config_file.loc[config_file.level == i,'Height'] = config_file.apply(lambda x: 
                                                                  x["Height"] if (x["Height"] > 0) 
                                                                  else (
                                                                    ((sum(config_file.parent_id==x["id"])+1)*buffer+
                                                                     sum(config_file.Height[config_file.parent_id==x["id"]]))
                                                                    if x["type"] == "System - Series"
                                                                    else (max(config_file.Height[config_file.parent_id==x["id"]])+2*buffer)), axis = 1)
  
  #step 3 - add parent mooN indicator
  config_file.m.replace(to_replace = 'None', value = 0)
  config_file.n.replace('None',0)
  config_file["mooNChild"] = config_file.parent_id.apply(lambda x: False if x==0 else config_file.m[config_file.id == x]>0)

  
  #step 4 . position the origin of the blocks on the RBD
  config_file["x"] = config_file.apply(lambda x: x["Width"]/2+buffer if x["level"] == 1 else 0, axis = 1)
  config_file["y"] = config_file.apply(lambda x: x["Height"]/2+buffer if x["level"] == 1 else 0, axis = 1)

  
  for i in range(2,max(config_file.level)+1):
    config_file.loc[config_file.level == i,'x'] = config_file.apply(lambda x:
                                                              (sum(config_file.x[config_file.id == x["parent_id"]]) -
                                                              sum(config_file.Width[config_file.id == x["parent_id"]])/2 +
                                                              sum(config_file.Width[(config_file.parent_id == x["parent_id"]) &
                                                                  (config_file.id < x["id"])]) +
                                                              (sum((config_file.parent_id == x["parent_id"]) &
                                                                  (config_file.id < x["id"]))+1)*buffer +
                                                              x["Width"]/2) 
                                                              if any(config_file.type[config_file.id == x["parent_id"]]=="System - Parallel")
                                                              else sum(config_file.x[config_file.id == x["parent_id"]]),axis = 1)
    config_file.loc[config_file.level == i,'y'] = config_file.apply(lambda x:
                                                              (sum(config_file.y[config_file.id == x["parent_id"]]) -
                                                              sum(config_file.Height[config_file.id == x["parent_id"]])/2 +
                                                              sum(config_file.Height[(config_file.parent_id == x["parent_id"]) &
                                                                  (config_file.id < x["id"])]) +
                                                              (sum((config_file.parent_id == x["parent_id"]) &
                                                                  (config_file.id < x["id"]))+1)*buffer +
                                                              x["Height"]/2) 
                                                              if any(config_file.type[config_file.id == x["parent_id"]]=="System - Series")
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
                                           ("parallel" if any(config_file.type[config_file.id == x["parent_id"]]=="System - Parallel") else "series")), axis=1)
  config_file["conn_to"] = config_file.apply(lambda x: None if x["conn"] is None else min(config_file.id[(config_file.parent_id == x["parent_id"]) & (config_file.id > x["id"])]), axis=1)

  result["config"] = config_file
  result["size"] = {'x':max(config_file.x2)+buffer,
                   'y':max(config_file.y2)+buffer}
  
  return(result)


#function to plot rbd and return a binary file for the image  
def draw_rbd_image(rbd_size, rbd_config):
  #define matplotlib figure and axis
  fig, ax = plt.subplots()
  
  #plot blocks
  for block_index in rbd_config.index:
    ax.add_patch(Rectangle((rbd_config.x[block_index]-rbd_config.Width[block_index]/2, rbd_config.y[block_index]-rbd_config.Height[block_index]/2), rbd_config.Width[block_index], rbd_config.Height[block_index], edgecolor = 'black'))
    ax.text(rbd_config.x[block_index], rbd_config.y[block_index]+rbd_config.Height[block_index]/2-0.5, rbd_config.tag[block_index], fontsize=6, horizontalalignment='center')

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



#TODO add ability to link fms to run time. if equipment is not running, pause modes