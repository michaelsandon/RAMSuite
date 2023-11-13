import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import app.static.helpers.global_formatting_functions as gff
import app.static.helpers.global_reliability_helpers as grh
from app.availability.static.helpers.ram_model_examples import new_rbd
from app.availability.static.helpers.availability_functions import helper_sample_from_dist as sfd
from datetime import datetime
from multiprocessing import Pool
from app.availability.static.helpers import ram_db_functions
import reliability.Other_functions as reloth

Blocktype = ["Equipment","System - Series", "System - Parallel"]


#function for compiling ram model
def compile_system_hierarchy(equipmentdf, subsystemdf, systemdf):
  #clean up cols
  compiled_system = systemdf
  while any(compiled_system["type"] == "Subsystem"):
    target_node = min(compiled_system.id[compiled_system.type=="Subsystem"])
    topdf = compiled_system[compiled_system.id < target_node].copy()
    bottomdf = compiled_system[compiled_system.id > target_node].copy()
    insertdf = subsystemdf[subsystemdf.subsystemid == compiled_system.refid.loc[compiled_system.id == target_node].values[0]].copy()
    insertdf["level"] = insertdf.level+compiled_system.level.loc[compiled_system.id == target_node].values[0]-1
    compiled_system = pd.concat([topdf,insertdf,bottomdf])
    compiled_system.reset_index(drop=True,inplace=True)
    compiled_system.id = compiled_system.index+1

  compiled_system.drop(['subsystemid','created_at'], axis=1, inplace=True)

  compiled_system["parent_id"] = compiled_system.apply(lambda x: 0  if(x["level"] ==1) else max(compiled_system.id[(compiled_system.id < x["id"]) & (compiled_system.level == (x["level"]-1))]), axis = 1)
  
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
  buffer = 1.5

  #Step 1. relate each child in the config file to it's parent
  if "id" not in config_file.columns:
    config_file.reset_index(inplace=True,drop=True)
    config_file["id"] = config_file.index

  if "parent_id" not in config_file.columns:
    config_file["parent_id"] = config_file.apply(lambda x: 0  if(x["level"] ==1) else     max(config_file.id[(config_file.id < x["id"]) & (config_file.level == (x["level"]-1))]), axis = 1)

  
  #step 2. define the height and width for each block in the file. Equipment blocks are a fixed size
  # the size of system blocks depend on the number of children and on the block type. Parallel blocks
  config_file["Width"] = config_file.type.apply(lambda x: 10 if (x=="Equipment") else 0)
  config_file["Height"] = config_file.type.apply(lambda x: 4 if (x=="Equipment") else 0)

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
    ax.text(rbd_config.x[block_index], rbd_config.y[block_index]+rbd_config.Height[block_index]/2-1, rbd_config.tag[block_index], fontsize=6, horizontalalignment='center')

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


#function to compile a RAM model
def compile_ram_model(equipmentdf, subsystemdf, systemdf, failuremodedf, inspectiondf, tbmdf, cbmdf, failuremoderesponsesdf):

  #create system hierarchy
  system_hierarchy = compile_system_hierarchy(equipmentdf, subsystemdf, systemdf)

  #join failure modes to equipment
  failuremodes = system_hierarchy.loc[system_hierarchy.type=="Equipment",["id","refid"]].merge(
    failuremodedf,right_on='equipmentid', left_on='refid', validate="m:m", suffixes=('eq','oldfm'), how='inner')
  failuremodes.reset_index(drop=True,inplace=True)
  failuremodes["idnewfm"] = failuremodes.index+1
  
  #join CBM responses with a subset df
  subsetdf = failuremodes.loc[:,["idnewfm","idoldfm"]].copy()
  cbmdf = subsetdf.join(cbmdf.set_index('target_fm'), on='idoldfm',validate='m:m',rsuffix='oldcbm',how='inner')
  cbmdf.reset_index(drop=True,inplace=True)
  cbmdf["idnewcbm"] = cbmdf.index+1
  cbmdf.rename(columns={"id": "idoldcbm"}, inplace=True)
  

  #join FM autoresponse df
  fmr = failuremoderesponsesdf.merge(failuremodes.loc[:,["idoldfm","idnewfm"]],left_on="failuremodeid",right_on="idoldfm")
  fmr = fmr.merge(cbmdf.loc[:,["idnewfm","idoldcbm","idnewcbm"]], left_on=["idnewfm","cbmid"], right_on=["idnewfm","idoldcbm"])
  fmr["id"] = fmr.index+1

  #clean up dfs
  eq_fm_map = failuremodes.loc[:,["ideq","idnewfm"]].rename(columns={"idnewfm":"fmid","ideq":"eqid"})
  
  failuremodes.rename(columns={"idnewfm":"id"}, inplace=True)
  failuremodes.drop(["ideq","created_at","refid","idoldfm"], axis=1, inplace=True)

  cbmdf.drop(["idoldfm","idoldcbm","created_at"], axis=1, inplace=True)
  cbmdf.rename(columns={"idnewcbm":"id","idnewfm":"target_fm"}, inplace=True)

  fmr.drop(["failuremodeid","cbmid","created_at","idoldfm","idoldcbm"], axis=1, inplace=True)
  fmr.rename(columns = {"idnewfm":"failuremodeid","idnewcbm":"cbmid"}, inplace=True)

  #create overall tag map
  tag_map_1 = system_hierarchy.loc[:,["id","tag","parent_id"]].copy()
  tag_map_1.rename(columns={"tag":"desc"}, inplace=True)
  tag_map_1["id"] = tag_map_1.id.apply(lambda x: "eq"+str(x))
  tag_map_1["parent_id"] = tag_map_1.parent_id.apply(lambda x: "eq"+str(x))
  tag_map_2 = failuremodes.loc[:,["id","desc"]].copy()
  tag_map_2["parent_id"] = tag_map_2.id.apply(lambda x: "eq"+str(eq_fm_map.loc[eq_fm_map.fmid==x,"eqid"].iloc[0]))
  tag_map_2["id"] = tag_map_2.id.apply(lambda x: "fm"+str(x))
  tag_map = pd.concat([tag_map_1,tag_map_2], ignore_index=True)
  
  result = {"hierarchy":system_hierarchy,
            "eq_fm_map":eq_fm_map,
            "tag_map":tag_map,
            "failuremodedf":failuremodes,
            "inspectiondf":inspectiondf,
            "tbmdf":tbmdf,
            "cbmdf":cbmdf,
            "failuremoderesponsesdf":fmr
           }

  return result



#TODO add ability to link fms to run time. if equipment is not running, pause modes

def run_rcm_simulation(failuremodedf, inspectiondf, tbmdf, cbmdf, inventorydf, failuremoderesponsesdf, componentlistdf, duration):

  #setup params ################
  curr_eq_lifetime_start_time = 0
  current_sim_time = 0

  #calculate the number of failure modes, inspection tasks, maintenance tasks
  n_fms = len(failuremodedf)
  #n_ins = len(inspectiondf)
  #n_tbm = len(tbmdf)
  n_mat = len(inventorydf)

  #modify ids to tags for sim
  failuremodedf["FM_tag"] = failuremodedf.id.apply(lambda x: "fm"+str(x))
  inventorydf["matl_tag"] = inventorydf.id.apply(lambda x: "matl"+str(x))

  #####predict initial TBF and TTD for all failure modes####


  column_names = ["FM_tag","TBF","TTD","Life_Start_Time", "Status", "VL_Start_Time", "TTF"]
  FM_curr_life_est = failuremodedf.copy()
  FM_curr_life_est[column_names]=None
  FM_curr_life_est["FM_tag"]=FM_curr_life_est.id.apply(lambda x: "fm"+str(x))
  FM_curr_life_est["Status"]="Operating"
  FM_curr_life_est["Life_Start_Time"]=0
  FM_curr_life_est["VL_Start_Time"]=0
  FM_curr_life_est["TBF"]=FM_curr_life_est.apply(lambda x: sfd(dist_as_dict={"dist":x["tbf_dist"],"par1":x["tbf_par1"],"par2":x["tbf_par2"],"par3":x["tbf_par3"]})[0], axis=1)
  FM_curr_life_est["TTD"]=FM_curr_life_est.apply(lambda x: sfd(dist_as_dict={"dist":x["ttd_dist"],"par1":x["ttd_par1"],"par2":x["ttd_par2"],"par3":x["ttd_par3"]})[0], axis=1)
  FM_curr_life_est["TTF"]=FM_curr_life_est.apply(lambda x:x["TBF"]+x["TTD"], axis=1)

  #create a dataframe with a column to hold the instantaneous availability for each failure mode
  FM_lifetimes = pd.DataFrame(columns=(["Time"]+list(FM_curr_life_est.FM_tag)))
  FM_lifetimes.loc[0] = [0]+[1]*n_fms

  #create a dataframe to hold material quantities #
  inventory_lifetimes = pd.DataFrame(columns=(["Time"]+list(inventorydf.matl_tag)))
  inventory_lifetimes.loc[0] = [0]+list(inventorydf.max_lvl)

  #not sure if inventory holding will be used
  #inventory_holding_lifetimes <- as.data.frame.matrix(matrix(nrow = 1, ncol = n_mat+1), stringsAsFactors = F)
  #names(inventory_holding_lifetimes) <- c("Time",inventory_holding_lifetimes$Materials)
  #inventory_holding_lifetimes[1,]<- 0

  #create inventory index
  inventory_log = inventorydf.loc[:,["matl_tag"]].copy()
  inventory_log["consumed"] = 0
  inventory_log["maintenance_delay"] = 0

  #create inventory backlog
  column_names = ["created","estimatedDeliveryTime","material","qty","allocated","holding"]
  inventory_backlog = pd.DataFrame(columns=column_names)

  #create CBM backlog
  maintenance_CBM_backlog = pd.DataFrame(columns = ["Due","cbmid"])
  

  #create Maintenance RTS backlog
  maintenance_RTS_backlog = pd.DataFrame(columns = ["FM_tag","Ref_task","Due","Reference_availability"])


  ####actual start of simulation#####
  Event_log_all = pd.DataFrame(columns=["Time","Desc","Event_Type","Details"])
  Event_log_all.loc[0] = {"Time":0,"Event_Type":"Simulation","Desc":"Simulation Start"}

  Inspection_log_all = pd.DataFrame(columns=["Time","Task","FM","Detection_Limit","Current_Condition","Findings","Action"])

  Maintenance_log_all = pd.DataFrame(columns=["Time","Task","Duration", "Details"])


  while(current_sim_time < duration):

    #start of loop
    next_event = find_next_event(
      #next_inspection_event = find_next_inspection_activity(inspection_sched),
      #next_TBM_maintenance_event = find_next_TBM_maintenance_activity(maintenance_sched_TBM),
      next_CBM_maintenance_event = find_next_CBM_maintenance_activity(maintenance_CBM_backlog.copy()),
      next_RTS_maintenance_event = find_next_RTS_maintenance_activity(maintenance_RTS_backlog.copy()),
      next_failure_event = find_next_failure_event(FM_curr_life_est = FM_curr_life_est.copy(), current_sim_time = current_sim_time, last_FM_lifetimes = FM_lifetimes.iloc[-1].copy()),
      next_Inv_event = find_next_Inv_Backlog_activity(inventory_backlog = inventory_backlog.copy()),
#next_isdp_event = find_next_ISDP_event(ISDP_df = ISDP_df, current_time = current_sim_time),
      dur = duration)

    next_sim_time = next_event["Time"]

    Event_log_all.loc[len(Event_log_all)] = next_event

    #print(paste0("Time:", next_event$Time,"Desc:",next_event$Desc))
    #process event
    if(next_event["Event_Type"] == "Inspection"):
      """
      FM_lifetimes <- increment_lifetimes(FM_lifetimes = FM_lifetimes,
                                          FM_curr_life_est = FM_curr_life_est,
                                          next_sim_time = next_sim_time)

      inspection_task_name <- next_event$Desc

      insp_results <- perform_inspection(inspection_task_name = inspection_task_name,
                                         insp_strategy = insp_strategy,
                                         FM_curr_life_est = FM_curr_life_est,
                                         inspection_time = next_sim_time)

      Inspection_log_all <- rbind(Inspection_log_all, insp_results)

      #TODO schedule next inspection
      #TODO account for cases where failure has occured and things need to be reset i.e. ignore life limits
      inspection_sched$Due[inspection_sched$Task_Name==inspection_task_name] <- calculate_next_inspection_due(last_insp_time = next_sim_time,
                                                                                                              freq = insp_strategy[[inspection_task_name]]$freq, 
                                                                                                              eq_life_lims =  insp_strategy[[inspection_task_name]]$eq_life_lims,
                                                                                                              life_at_last_insp = next_sim_time - curr_eq_lifetime_start_time)

      #TODO add CBM from inspection to the CBM maintenance backlog
      Actions <- insp_results %>% filter(!is.na(Action))
      if(nrow(Actions)>0){
        for(i in 1:nrow(Actions)){
          maintenance_CBM_backlog[nrow(maintenance_CBM_backlog)+1,] <- NA
          maintenance_CBM_backlog$Resp[nrow(maintenance_CBM_backlog)] <- Actions$Action[i]
          maintenance_CBM_backlog$Due[nrow(maintenance_CBM_backlog)] <- next_sim_time
        }
      }
      """
    elif (next_event["Event_Type"] == "Maintenance_TBM"):
      """
      FM_lifetimes <- increment_lifetimes(FM_lifetimes = FM_lifetimes,
                                          FM_curr_life_est = FM_curr_life_est,
                                          next_sim_time = next_sim_time)

      FM_lifetimes <- increment_lifetimes(FM_lifetimes = FM_lifetimes,
                                          FM_curr_life_est = FM_curr_life_est,
                                          next_sim_time = next_sim_time)

      maintenance_task_name <- next_event$Desc
      maintenance_task_details <- maint_strategy$TBM[[maintenance_task_name]]

      #Perform Maintenance
      maintenance_result <- perform_maintenance(maintenance_task_details = maintenance_task_details,
                                                maintenance_time = next_sim_time,
                                                maintenance_RTS_backlog = maintenance_RTS_backlog,
                                                FM_curr_life_est = FM_curr_life_est,
                                                FM_lifetimes = FM_lifetimes,
                                                inventory_lifetimes = inventory_lifetimes,
                                                inventory_index = inventory_index,
                                                inventory_backlog = inventory_backlog,
                                                ISDP_DF = ISDP_df,
                                                duration = duration)
      maintenance_RTS_backlog <- maintenance_result$maintenance_RTS_backlog
      inventory_lifetimes <- maintenance_result$inventory_lifetimes
      inventory_backlog <- maintenance_result$inventory_backlog

      FM_curr_life_est <- maintenance_result$FM_curr_life_est
      FM_lifetimes <- maintenance_result$FM_lifetimes

      #Reset TBM Schedule
      maintenance_sched_TBM$Due[maintenance_sched_TBM$Task_Name==maintenance_task_name] <- calculate_next_maintenance_due(last_maint_time = next_sim_time,
                                                                                                                          freq = maintenance_task_details$freq, 
                                                                                                                          eq_life_lims =  maintenance_task_details$eq_life_lims,
                                                                                                                          life_at_last_maint = next_sim_time - curr_eq_lifetime_start_time)
      """
    elif (next_event["Event_Type"] == "Maintenance_CBM"):

      Maintenance_log_all.loc[len(Maintenance_log_all)] = {"Time":next_sim_time,
                                                          "Task":"cbm_"+str(next_event["Details"]["cbmid"]),
                                                           "Details":next_event["Details"]
                                                           }
      
      maintenance_task_details = cbmdf.loc[cbmdf.id == next_event["Details"]["cbmid"]].head(1).to_dict(orient='records')[0]

      FM_lifetimes = increment_lifetimes(FM_lifetimes = FM_lifetimes.copy(),
                                         FM_curr_life_est = FM_curr_life_est.copy(),
                                         next_sim_time = next_sim_time)
      FM_lifetimes = increment_lifetimes(FM_lifetimes = FM_lifetimes.copy(),
                                         FM_curr_life_est = FM_curr_life_est.copy(),
                                         next_sim_time = next_sim_time)

      #Perform Maintenance
      maintenance_result = perform_maintenance(maintenance_task_details = maintenance_task_details,
                                               component_list_details=componentlistdf[componentlistdf.listid==maintenance_task_details["component_list_id"]].copy(),
                                              maintenance_time = next_sim_time,
                                              maintenance_RTS_backlog = maintenance_RTS_backlog,
                                              FM_curr_life_est = FM_curr_life_est,
                                              FM_lifetimes = FM_lifetimes,
                                              inventory_lifetimes = inventory_lifetimes,
                                              inventorydf = inventorydf,
                                              inventory_backlog = inventory_backlog,
                                              ISDP_DF = None,#ISDP_df,
                                              duration = duration,
                                              Maintenance_log_all = Maintenance_log_all,
                                              inventory_log = inventory_log)
      maintenance_RTS_backlog = maintenance_result["maintenance_RTS_backlog"].copy()
      inventory_lifetimes = maintenance_result["inventory_lifetimes"].copy()
      inventory_backlog = maintenance_result["inventory_backlog"].copy()
      FM_curr_life_est = maintenance_result["FM_curr_life_est"].copy()
      FM_lifetimes = maintenance_result["FM_lifetimes"].copy()


      #remove CBM maintenance from the backlog
      maintenance_CBM_backlog.drop(index = maintenance_CBM_backlog.index[maintenance_CBM_backlog.cbmid == next_event["Details"]["cbmid"]], inplace=True) #remove all instances of the task.

    elif (next_event["Event_Type"] == "Maintenance_RTS"):

      FM_lifetimes = increment_lifetimes(FM_lifetimes = FM_lifetimes.copy(),
         FM_curr_life_est = FM_curr_life_est.copy(),
         next_sim_time = next_sim_time)
      FM_lifetimes = increment_lifetimes(FM_lifetimes = FM_lifetimes.copy(),
         FM_curr_life_est = FM_curr_life_est.copy(),
         next_sim_time = next_sim_time)

      RTS_event = next_event["Details"]

      RTS_result = perform_RTS(FM_curr_life_est = FM_curr_life_est,FM_lifetimes = FM_lifetimes, RTS_time = next_sim_time, RTS_event = RTS_event)

      FM_curr_life_est = RTS_result["FM_curr_life_est"].copy()
      FM_lifetimes = RTS_result["FM_lifetimes"].copy()

      #remove RTS event from RTS backlog
      maintenance_RTS_backlog.drop(index = maintenance_RTS_backlog.index[maintenance_RTS_backlog.FM_tag == RTS_event["FM_tag"]], inplace=True) #remove all instances of the task.

    elif (next_event["Event_Type"] == "Fault"):
      FM_curr_life_est.loc[FM_curr_life_est.FM_tag == next_event["Details"]["FM_tag"],"Status"] = "Fault"
      FM_lifetimes = increment_lifetimes(FM_lifetimes = FM_lifetimes.copy(),
                                         FM_curr_life_est = FM_curr_life_est.copy(),
                                         next_sim_time = next_sim_time)
    elif (next_event["Event_Type"] == "Fail"):
      
      FM_curr_life_est.loc[FM_curr_life_est.FM_tag == next_event["Details"]["FM_tag"],"Status"] = "Fail"
      FM_lifetimes = increment_lifetimes(FM_lifetimes = FM_lifetimes.copy(),
                                          FM_curr_life_est = FM_curr_life_est.copy(),
                                          next_sim_time = next_sim_time)

      #schedule repair maintenance if required
      required_responses = failuremoderesponsesdf[failuremoderesponsesdf.failuremodeid==next_event["Details"]["id"]]
      if(len(required_responses)>0):
        for id in required_responses.cbmid:
          maintenance_CBM_backlog.loc[len(maintenance_CBM_backlog)] = {"Due":next_sim_time, "cbmid":id}

    elif (next_event["Event_Type"] =="Inventory_backlog"):

      inventory_lifetimes.loc[len(inventory_lifetimes)] = inventory_lifetimes.tail(1).to_dict(orient="records")[0]
      inventory_lifetimes.loc[len(inventory_lifetimes)-1,"Time"] = next_sim_time
      inventory_lifetimes.loc[len(inventory_lifetimes)] = inventory_lifetimes.tail(1).to_dict(orient="records")[0]

      #stock if required
      inv_event = next_event["Details"]
      if(inv_event["qty"] > inv_event["allocated"]):
        inventory_lifetimes.loc[len(inventory_lifetimes)-1,inv_event["material"]] = inventory_lifetimes[inv_event["material"]].iloc[-1] + (inv_event["qty"] - inv_event["allocated"])

      #remove row from inv backlog
      #upgrade this process to an order ID approach
      inventory_backlog.drop(index = inventory_backlog.sort_values(by=["estimatedDeliveryTime"],ascending=True).head(1).index, inplace=True)
      inventory_backlog.reset_index(drop=True,inplace=True)


    elif (next_event["Event_Type"] == "ISDP"):
      """
      FM_lifetimes <- increment_lifetimes(FM_lifetimes = FM_lifetimes,
                                          FM_curr_life_est = FM_curr_life_est,
                                          next_sim_time = next_sim_time)

      start_stop <- str_split(string = next_event$Desc, pattern = ";")[[1]][2]
      isdp_id <- str_split(string = next_event$Desc, pattern = ";")[[1]][1] %>% as.numeric()

      if(start_stop=="Start"){
        ISDP_df$start_ind[ISDP_df$ID==isdp_id] <- "Y"
      } else {
        ISDP_df$stop_ind[ISDP_df$ID==isdp_id] <- "Y"
      }

      ISDP_results <- process_ISDP_event(ISDP_event_id = isdp_id,
                                         start_or_stop = start_stop,
                                         ISDP_df = ISDP_df, 
                                         FM_lifetimes = FM_lifetimes,
                                         FM_curr_life_est = FM_curr_life_est,
                                         event_time = next_sim_time,
                                         maintenance_RTS_backlog = maintenance_RTS_backlog)

      FM_lifetimes <- ISDP_results$FM_lifetimes
      FM_curr_life_est <- ISDP_results$FM_curr_life_est
      maintenance_RTS_backlog <- ISDP_results$maintenance_RTS_backlog
      ISDP_df <- ISDP_results$ISDP_df

      """
    elif (next_event["Event_Type"] == "Simulation"):
      FM_lifetimes = increment_lifetimes(FM_lifetimes = FM_lifetimes.copy(), FM_curr_life_est = FM_curr_life_est.copy(),       next_sim_time = duration)
      inventory_lifetimes.loc[len(inventory_lifetimes)] = inventory_lifetimes.tail(1).to_dict(orient='records')[0]
      inventory_lifetimes.loc[len(inventory_lifetimes)-1,"Time"] = duration

    #increment time
    current_sim_time = next_sim_time
  
  result = {
    "FM_lifetimes": FM_lifetimes,
    "Event_log_all": Event_log_all,
    "Inspection_log_all": Inspection_log_all,
    "Maintenance_log_all": Maintenance_log_all,
    "inventory_lifetimes": inventory_lifetimes,
    "inventory_log": inventory_log
  }

  return result


#helper function to increment the lifetime dataframe
def increment_lifetimes(FM_lifetimes, FM_curr_life_est, next_sim_time):
  new_row = {}
  new_row["Time"]= next_sim_time
  for i in range(len(FM_curr_life_est)):
    status = FM_curr_life_est.Status.loc[i]
    tag = FM_curr_life_est.FM_tag.loc[i]
    last_av = FM_lifetimes[tag].iloc[-1]


    if(status in ["Operating","Under_Maintenance"]):
      new_row[tag]=last_av
    elif(status == "Fault" and last_av==0):
      new_row[tag]=last_av
    elif(status == "Fault"):
      VL_Start_Time = FM_curr_life_est.VL_Start_Time.loc[i]
      TBF = FM_curr_life_est.TBF.loc[i]
      TTD = FM_curr_life_est.TTD.loc[i]
      t = next_sim_time 

      abs_tbf = VL_Start_Time + TBF
      abs_ttd = VL_Start_Time + TBF + TTD

      if(t<=abs_tbf):
        new_row[tag]=last_av #1 carry through last observation instead of 1
      elif(t <= abs_ttd and t >= abs_tbf):
        #TODO
        new_row[tag]= max(last_av - (t-abs_tbf)/TTD, 0) #+ (abs_ttd-t)/TTD #(-1)/(abs_ttd - abs_tbf)*(t-abs_tbf)+1
      else:
        new_row[tag]=0

    elif(status == "Fail"):
      new_row[tag]=0

  FM_lifetimes.loc[len(FM_lifetimes)] = new_row

  return(FM_lifetimes)

#helper function to determin the next fail event
def find_next_failure_event(FM_curr_life_est, current_sim_time, last_FM_lifetimes):
  if(len(FM_curr_life_est)==0):
    result = None
  else:

    #Define time until fault starts
    fault_times = FM_curr_life_est.copy()
    fault_times["Time"] = fault_times.apply(lambda x:x["VL_Start_Time"]+x["TBF"], axis=1)
    
    fail_times = FM_curr_life_est.copy()
    fail_times["Time"] = fail_times.apply(lambda x:x["VL_Start_Time"]+x["TBF"]+last_FM_lifetimes[x["FM_tag"]]*x["TTD"], axis=1) #fail time should be moderated by the current "availability value of the asset"

    if any(fault_times["Time"]>current_sim_time):
      next_fault = fault_times[fault_times["Time"]>current_sim_time].sort_values(by=["Time"]).head(1).iloc[0]
    else:
      next_fault = None

    if any(fail_times["Time"]>current_sim_time):
      next_fail = fail_times[fail_times["Time"]>current_sim_time].sort_values(by=["Time"]).head(1).iloc[0]
    else:
      next_fail = None

    if next_fault is None and next_fail is None:
      result = None#{"Time": None, "FM_tag": None, "Event_Type": None}
    elif next_fault is None:
      result = {"Time": next_fail["Time"], "Details": next_fail, "Event_Type": "Fail"}
    elif next_fail is None:
      result = {"Time": next_fault["Time"], "Details": next_fault, "Event_Type": "Fault"}
    elif next_fail["Time"]<next_fault["Time"]:
      result = {"Time": next_fail["Time"], "Details": next_fail, "Event_Type": "Fail"}
    else:
      result = {"Time": next_fault["Time"], "Details": next_fault, "Event_Type": "Fault"}
    
  return(result)


#helper function to determine next CBM Event
def find_next_CBM_maintenance_activity(maintenance_CBM_backlog):
  if(len(maintenance_CBM_backlog)==0):
    result = None
  else:
    result = {}
    result["Details"] = maintenance_CBM_backlog.sort_values(by=["Due"],ascending=True).head(1).to_dict(orient='records')[0].copy()
    result["Event_Type"] = "Maintenance_CBM"
    result["Time"] = result["Details"]["Due"]

  return(result)

#helper function to determine next RTS event
def find_next_RTS_maintenance_activity(maintenance_RTS_backlog):
  if(len(maintenance_RTS_backlog)==0):
    result = None
  else:
    result = {}
    result["Details"] = maintenance_RTS_backlog.sort_values(by=["Due"],ascending=True).head(1).to_dict(orient='records')[0]
    result["Event_Type"] = "Maintenance_RTS"
    result["Time"] = result["Details"]["Due"]
    

  return(result)

#helper function to determine next inventory stocking
def find_next_Inv_Backlog_activity(inventory_backlog):
  if(len(inventory_backlog)==0):
    result = None
  else:
    result = {}
    result["Details"] = inventory_backlog.sort_values(by=["estimatedDeliveryTime"],ascending=True).head(1).to_dict(orient='records')[0]
    result["Event_Type"] = "Inventory_backlog"
    result["Time"] = result["Details"]["estimatedDeliveryTime"]

  return(result)


#helper function to determine next event
def find_next_event(dur, next_failure_event, next_inspection_event = None, next_TBM_maintenance_event = None,
                    next_CBM_maintenance_event=None,next_RTS_maintenance_event= None, next_Inv_event=None,
                    next_isdp_event = None):

  result_df = pd.DataFrame(columns = ["Time","Event_Type","Details"])

  result_df.loc[len(result_df)] = next_failure_event

  result_df.loc[len(result_df)] = next_inspection_event

  result_df.loc[len(result_df)] = next_TBM_maintenance_event

  result_df.loc[len(result_df)] = next_CBM_maintenance_event

  result_df.loc[len(result_df)] = next_RTS_maintenance_event

  result_df.loc[len(result_df)] = next_Inv_event

  result_df.loc[len(result_df)] = next_isdp_event

  result_df.loc[len(result_df)] = next_isdp_event

  result_df.loc[len(result_df)] = {"Time": dur, "Details": {"Desc":"Sim End"}, "Event_Type": "Simulation"}

  #take the first event
  result = result_df.sort_values(by=["Time"], ascending = True).head(1).to_dict(orient="records")[0]

  return(result)


#helper Perform Maintenance
def perform_maintenance(maintenance_task_details, component_list_details, maintenance_time, maintenance_RTS_backlog, FM_curr_life_est, FM_lifetimes, inventory_lifetimes, inventorydf, inventory_backlog, ISDP_DF,duration, Maintenance_log_all, inventory_log):

  #check material availability and use this to calculate the material delay that will add to the RTS time######
  mat_delay = 0
  if(maintenance_task_details["component_list_id"] is not None):
    requirements = component_list_details.loc[component_list_details.listid == maintenance_task_details["component_list_id"]].copy()
    
    for m in requirements.index:
      req_materialid = requirements.materialid[m]
      req_material_tag = "matl"+str(req_materialid)
      req_q = requirements.loc[m,"qty"]#requirements.qty[m]

      #inventory_log
      inventory_log.loc[inventory_log.matl_tag == req_material_tag,"consumed"] = inventory_log.loc[inventory_log.matl_tag == req_material_tag,"consumed"] + req_q

      tmp_qty = inventory_lifetimes[req_material_tag].iloc[-1]

      #take stock from warehouse first
      if(req_q > tmp_qty):
        req_q = req_q - tmp_qty
        new_tmp_qty = 0
      else:
        new_tmp_qty = tmp_qty - req_q
        req_q = 0

      inventory_lifetimes.loc[len(inventory_lifetimes)] = inventory_lifetimes.iloc[-1].copy()
      inventory_lifetimes["Time"].iloc[-1] = maintenance_time
      inventory_lifetimes.loc[len(inventory_lifetimes)] = inventory_lifetimes.iloc[-1].copy()
      inventory_lifetimes.loc[len(inventory_lifetimes)-1,req_material_tag] = new_tmp_qty
      #if min stock reached and was previously over place order
      matl_min = inventorydf.loc[inventorydf.matl_tag == req_material_tag]["min_lvl"].iloc[0]
      matl_max = inventorydf.loc[inventorydf.matl_tag == req_material_tag]["max_lvl"].iloc[0]


      if((new_tmp_qty <= matl_min) & (tmp_qty > matl_min)):
        #order the deficit to meet the max
        new_order = {"created":maintenance_time,
                     "estimatedDeliveryTime":maintenance_time+inventorydf.loc[inventorydf.matl_tag == req_material_tag]["leadtime"].iloc[0],
                     "material":req_material_tag,
                     "qty":matl_max-new_tmp_qty,
                     "allocated":0}
        inventory_backlog.loc[len(inventory_backlog)] = new_order
  
      elif(tmp_qty <= matl_min):
        #order amount that will be used
        new_order = {"created":maintenance_time,
                     "estimatedDeliveryTime":maintenance_time+inventorydf.loc[inventorydf.matl_tag == req_material_tag]["leadtime"].iloc[0],
                     "material":req_material_tag,
                     "qty":requirements.qty[m], ###not sure about this
                     "allocated":0}
        inventory_backlog.loc[len(inventory_backlog)] = new_order

      # use the required qty on backorder to update the "allocated amount to orders" of items in the order backlog
      while((req_q > 0) & (len(inventory_backlog.loc[(inventory_backlog.material == req_material_tag) & (inventory_backlog.allocated < inventory_backlog.qty)])>0)):
        target_id = inventory_backlog.loc[(inventory_backlog.material == req_material_tag) & (inventory_backlog.allocated < inventory_backlog.qty)].index[0]  
        tmpdelta = min(req_q,inventory_backlog.qty[target_id]-inventory_backlog.allocated[target_id])
        req_q = req_q - tmpdelta
        inventory_backlog.loc[target_id,"allocated"] = inventory_backlog.loc[target_id,"allocated"] + tmpdelta
        tmp_mat_delay = mat_delay
        mat_delay = max(inventory_backlog.estimatedDeliveryTime[target_id]-maintenance_time,mat_delay)
        if mat_delay != tmp_mat_delay:
          mat_delay_cause = req_material_tag

    if mat_delay != 0:
      inventory_log.loc[inventory_log.matl_tag == mat_delay_cause,"maintenance_delay"] = inventory_log.loc[inventory_log.matl_tag == mat_delay_cause,"maintenance_delay"] + mat_delay
      
        #if this still doesn't satify all req materials debug
  # material delay calcs done
  
  #start the maintenance .... need to scehdule the effect of the maintenance to happen#####
  #for repairs, schedule the repair to be complete at a certain time. or schedule the
  FM_tag = "fm"+str(maintenance_task_details["target_fm"])
  FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag, "Status"] = "Under_Maintenance"

  ref_a = FM_lifetimes[FM_tag].iloc[-1]

  if(maintenance_task_details["executed_offline"]):
    FM_lifetimes.loc[len(FM_lifetimes)-1,FM_tag]= 0

  expected_return = maintenance_time + maintenance_task_details["active_maint_time"] + mat_delay

  """
  #check ISDP intersections
  if(str_detect(maintenance_task_details$Affected_Modes[i], pattern = "_") & nrow(ISDP_DF)>0){
    tmp_isdp <- ISDP_DF %>% filter(node_id == as.numeric(str_split(string = maintenance_task_details$Affected_Modes[i], pattern = "_")[[1]][1])) %>% 
      filter(expected_return >= start_t & expected_return <= end_t)
    if(nrow(tmp_isdp)==1){
      expected_return <- max(tmp_isdp$end_t, expected_return)
    }
  }


  if(!is.null(maintenance_task_details$ISDP_rqd)){
    if(maintenance_task_details$ISDP_rqd == "Y"){
      tmp_isdp <- ISDP_DF %>% filter(node_id == as.numeric(str_split(string = maintenance_task_details$Affected_Modes[i], pattern = "_")[[1]][1])) %>% 
        filter(expected_return <= end_t)
      if(nrow(tmp_isdp)==0){
        expected_return <- duration
      } else {
        expected_return <- tmp_isdp$end_t[which.min(tmp_isdp$end_t)]
      }
    }
  }
  """

  new_RTS = {"FM_tag":FM_tag,"Ref_task":maintenance_task_details,"Due":expected_return,"Reference_availability":ref_a}

  maintenance_RTS_backlog.loc[len(maintenance_RTS_backlog)] = new_RTS
  #
  Maintenance_log_all.loc[len(Maintenance_log_all)-1,"Duration"] = expected_return - maintenance_time

  
  return ({"maintenance_RTS_backlog": maintenance_RTS_backlog,
          "FM_curr_life_est": FM_curr_life_est,
          "FM_lifetimes": FM_lifetimes,
          "inventory_lifetimes": inventory_lifetimes,
          "inventory_backlog": inventory_backlog})





#helper function for Performing RTS
def perform_RTS(RTS_event, FM_curr_life_est, FM_lifetimes, RTS_time):
  task_detail = RTS_event["Ref_task"]
  FM_tag = RTS_event["FM_tag"]
  ref_a = RTS_event["Reference_availability"]

  #change Availability value
  if (task_detail["availability_after_maintenance_is_abs"]):
    new_av = max(min(task_detail["availability_after_maint"],1),0)
  else:
    new_av = max(min(task_detail["availability_after_maint"]+RTS_event["Reference_availabiity"],1),0)

  FM_lifetimes.loc[len(FM_lifetimes)-1,FM_tag]=new_av

  #change virtual life value
  # if virtual life needs to be reset to an absolute reference do the following
  curr_VL_start = FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag, "VL_Start_Time"]
  curr_VL = RTS_time-curr_VL_start
  curr_L_start = FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag, "Life_Start_Time"]
  
  if (task_detail["virtual_life_after_maint_is_abs"]):
    new_VL = task_detail["virtual_life_after_maint"]
  else:
    new_VL = max(task_detail["virtual_life_after_maint"]+curr_VL,curr_VL)

  new_VL_start = RTS_time - new_VL
  FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag, "VL_Start_Time"] = new_VL_start

  #estimate new TBF TTD parameters and reset life start if needed
  #TODO work on this criteria
  
  if((ref_a == 0) | (new_av == 1)):
    #reset life start
    FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag, "Life_Start_Time"] = RTS_time
    rr = FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag].to_dict(orient='records')[0]
    #forecast new life
    FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag,"TBF"]= sfd(dist_as_dict={"dist":rr["tbf_dist"],
                                                                                     "par1":rr["tbf_par1"],
                                                                                     "par2":rr["tbf_par2"],
                                                                                     "par3":rr["tbf_par3"]})[0]
    FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag,"TTD"]= sfd(dist_as_dict={"dist":rr["ttd_dist"],
                                                                                   "par1":rr["ttd_par1"],
                                                                                   "par2":rr["ttd_par2"],
                                                                                   "par3":rr["ttd_par3"]})[0]
    FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag,"TTF"]=FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag,"TBF"]+FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag,"TTD"]

  #set status to operating
  FM_curr_life_est.loc[FM_curr_life_est.FM_tag == FM_tag,"Status"] = "Operating"
  

  return({"FM_curr_life_est": FM_curr_life_est, "FM_lifetimes": FM_lifetimes})





def eval_eq_lifetimes(FM_Lifetimes, eq_fm_map,hierarchy):


  eqblocks = hierarchy.loc[hierarchy.type == 'Equipment',"id"].to_list()
  for eqid in eqblocks:
    if len(eq_fm_map.loc[eq_fm_map.eqid==eqid])==0:
      FM_Lifetimes["eq"+str(eqid)] = 1
    else:
      fmids = eq_fm_map.loc[eq_fm_map.eqid==eqid,"fmid"].to_list()
      fmtags = ["fm"+str(fmid) for fmid in fmids]
      FM_Lifetimes["eq"+str(eqid)] = FM_Lifetimes.apply(lambda x:min(x[fmtags]), axis=1)
    
  for i in range(max(hierarchy.level),0,-1):
    sysblocks = hierarchy.loc[(hierarchy.level==i)&(hierarchy.type != "Equipment"),"id"].to_list()
    for blockid in sysblocks:
      childids = hierarchy.loc[hierarchy.parent_id==blockid,"id"].to_list()
      childtags = ["eq"+str(id) for id in childids]
      blocktype = hierarchy.loc[hierarchy.id==blockid,"type"].iloc[0]
      if blocktype == "System - Series":
        FM_Lifetimes["eq"+str(blockid)] = FM_Lifetimes.apply(lambda x:min(x[childtags]), axis=1)
      else:
        m = hierarchy.loc[hierarchy.id==blockid,"m"].iloc[0]
        n = hierarchy.loc[hierarchy.id==blockid,"n"].iloc[0]
        if pd.isna(m):
          m = len(childids)

        FM_Lifetimes["eq"+str(blockid)] = FM_Lifetimes.apply(lambda x:1 if sum(x[childtags]==1)>=m else 0, axis=1)

  return FM_Lifetimes
      
        
def eval_criticalities(FM_Lifetimes, eq_fm_map, hierarchy, reference_av, sim_id):
  columns = FM_Lifetimes.columns.to_list()
  columns.remove("Time")
  result = pd.DataFrame(columns = columns)
  result.loc[len(result)] = 0
    

  for block in columns:
    lifetimes = FM_Lifetimes.copy()
    lifetimes.loc[:,block] = 1

    curr_block = block

    if block[0:2] == "fm":
      parent_id = eq_fm_map.loc[eq_fm_map.fmid == int(curr_block[2:]),"eqid"].iloc[0]
    else:
      parent_id = hierarchy.loc[hierarchy.id == int(curr_block[2:]),"parent_id"].iloc[0]
    
    while parent_id != 0:
      block_to_eval = parent_id
      blocktype = hierarchy.loc[hierarchy.id==block_to_eval,"type"].iloc[0]
      if blocktype == "Equipment":
        if len(eq_fm_map.loc[eq_fm_map.eqid==block_to_eval])==0:
          lifetimes["eq"+str(block_to_eval)] = 1
        else:
          fmids = eq_fm_map.loc[eq_fm_map.eqid==block_to_eval,"fmid"].to_list()
          fmtags = ["fm"+str(fmid) for fmid in fmids]
          lifetimes["eq"+str(block_to_eval)] = lifetimes.apply(lambda x:min(x[fmtags]), axis=1)
      else:
        childids = hierarchy.loc[hierarchy.parent_id==block_to_eval,"id"].to_list()
        childtags = ["eq"+str(id) for id in childids]
        if blocktype == "System - Series":
          lifetimes["eq"+str(block_to_eval)] = lifetimes.apply(lambda x:min(x[childtags]), axis=1)
        else:
          m = hierarchy.loc[hierarchy.id==block_to_eval,"m"].iloc[0]
          n = hierarchy.loc[hierarchy.id==block_to_eval,"n"].iloc[0]
          if pd.isna(m):
            m = len(childids)
          lifetimes["eq"+str(block_to_eval)] = lifetimes.apply(lambda x:1 if sum(x[childtags]==1)>=m else 0, axis=1)
      parent_id = hierarchy.loc[hierarchy.id == block_to_eval,"parent_id"].iloc[0]

    #perform integration
    new_p_p = grh.process_uptime_signals(lifetimes.loc[:,["Time","eq1"]].copy()).loc[0,"uptime_%"]
    delta_p_p = new_p_p-reference_av
    if reference_av == 1:
      crit = 0
    else:
      crit = (delta_p_p)/(1 - reference_av)

    result.loc[0,block] = crit

  if sim_id is not None:
    result["sim_id"] = sim_id

  return result
    
        
        
    
    

#final function option 1
def run_ram_model(equipmentdf, subsystemdf, systemdf, failuremodedf, inspectiondf, tbmdf, cbmdf, failuremoderesponsesdf, inventorydf, componentlistdf, duration,n_sims,updates = None):

  start_timestamp = datetime.now()


  #compile model and receive result
  compiled_model = compile_ram_model(equipmentdf, subsystemdf, systemdf, failuremodedf,
                                     inspectiondf, tbmdf, cbmdf, failuremoderesponsesdf)
    
  hierarchydf = compiled_model["hierarchy"]
  eq_fm_map = compiled_model["eq_fm_map"]
  failuremodedf = compiled_model["failuremodedf"]
  inspectiondf = compiled_model["inspectiondf"]
  tbmdf = compiled_model["tbmdf"]
  cbmdf = compiled_model["cbmdf"]
  failuremoderesponsesdf = compiled_model["failuremoderesponsesdf"]
  compiled_timestamp = datetime.now()

  #update state
  if updates is not None:
    task_obj = updates[0]
    meta = updates[1]
    meta["current"]=2
    task_obj.update_state(meta=meta)
    meta.update({"status":"Simulating","total":n_sims, "current":0})
    task_obj.update_state(meta=meta)

  details = []
  for i in range(n_sims):
    sim_details = run_rcm_simulation(failuremodedf, inspectiondf, tbmdf, cbmdf, inventorydf,
                                     failuremoderesponsesdf, componentlistdf, duration)

    #add in result post processing potentially
    details.append(sim_details)
    if updates is not None:
      meta["current"]=i
      task_obj.update_state(meta=meta)

  #timestamp end of simulation
  simulated_timestamp = datetime.now()

  #update state
  if updates is not None:
    meta.update({"status":"Post Processing Results","total":n_sims, "current":0})

  #process results
  for i in range(len(details)):
    sim_details = details[i]

    #manage lifetimes
    lifetimes = sim_details["FM_lifetimes"].copy()
    lifetimes = eval_eq_lifetimes(FM_Lifetimes = lifetimes, eq_fm_map= eq_fm_map.copy(), hierarchy = hierarchydf.copy())
    details[i]["FM_lifetimes"] = lifetimes.copy()
    
    if updates is not None:
      meta["current"]=i
      task_obj.update_state(meta=meta)

    """
    "FM_lifetimes": FM_lifetimes,
    "Event_log_all": Event_log_all,
    "Inspection_log_all": Inspection_log_all,
    "inventory_lifetimes": inventory_lifetimes,
    "inv_details": None #inv_details
    """
  
  stats = {"Sys_Av":[],
          "Sys_Av_Stats":[],
           "Eq_Av":[],
           "Eq_Av_Stats":[],
          "Inv":[],
          "Inv_Stats":[],
          "Eq_Crit":[],
          "Eq_Crit_Stats":[],
          "Maint":[],
          "Maint_Stats":[]}

  inv_p1 = []
  inv_p2 = []
  #update state
  if updates is not None:
    meta.update({"status":"Evaluating stats","total":n_sims, "current":0})
    task_obj.update_state(meta=meta)
    
  for i in range(len(details)):
    #process results
    #calculate the mean production uptime for each sim
    stats['Sys_Av'].append(grh.process_uptime_signals(details[i]["FM_lifetimes"].loc[:,["Time","eq1"]].copy(),signaltype="eq",sim_id=i+1).drop(columns=["signalid"]))

    #calculate the mean uptime for each node in each sim
    stats['Eq_Av'].append(grh.process_uptime_signals(details[i]["FM_lifetimes"].copy(), signaltype="eq",sim_id=i+1))

    #calculate the mean inventory value for each sim & stockout events
    inv_p1.append(grh.process_uptime_signals(details[i]["inventory_lifetimes"].copy(),signaltype="matl",sim_id=i+1).melt(id_vars=["matl","sim_id"]))

    #inventory consumption
    inv_log = details[i]["inventory_log"].melt(id_vars=["matl_tag"]).rename(columns={"matl_tag":"matl"})
    inv_log["sim_id"] = i+1
    inv_p2.append(inv_log)
    
    #calculate the criticality of each node for each sim
    stats["Eq_Crit"].append(eval_criticalities(FM_Lifetimes = details[i]["FM_lifetimes"].copy(), eq_fm_map = eq_fm_map.copy(), hierarchy = hierarchydf.copy(), reference_av = stats['Sys_Av'][i].loc[0,"uptime_%"], sim_id = i))

    #append subset of maintenance log
    m_i = details[i]["Maintenance_log_all"].loc[:,["Task","Duration"]].copy()
    m_i["sim_id"] = i+1
    stats["Maint"].append(m_i)
    
    if updates is not None:
      meta["current"]=i
      task_obj.update_state(meta=meta)

  
  stats["Sys_Av"] = pd.concat(stats["Sys_Av"], ignore_index=True)
  stats["Sys_Av_Stats"] = stats["Sys_Av"].describe().drop(['count'], axis = 0).drop(['sim_id'], axis = 1)
  
  stats["Eq_Av"] = pd.concat(stats["Eq_Av"], ignore_index=True)
  stats["Eq_Av_Stats"] = stats["Eq_Av"].drop(["sim_id"], axis=1).melt(id_vars=["signalid"]).groupby(["signalid","variable"]).describe().drop([("value","count")], axis=1)
  stats["Eq_Av_Stats"].columns = stats["Eq_Av_Stats"].columns.droplevel(0)
    
  #stats["Inv_Av"] = pd.concat(stats["Inv_Av"], ignore_index=True)
  #stats["Inv_Av_Stats"] = stats["Inv_Av"].drop(["sim_id"], axis=1).melt(id_vars=["matl"]).groupby(["matl","variable"]).describe().drop([("value","count")], axis=1)
  stats["Inv"] = pd.concat(inv_p1+inv_p2, ignore_index=True)
  stats["Inv_Stats"] = stats["Inv"].drop(["sim_id"], axis=1).groupby(["matl","variable"]).describe().drop([("value","count")], axis=1)
  stats["Inv_Stats"].columns = stats["Inv_Stats"].columns.droplevel(0)
  
  stats["Eq_Crit"] = pd.concat(stats["Eq_Crit"], ignore_index=True)
  stats["Eq_Crit_Stats"] = stats["Eq_Crit"].drop(["sim_id"], axis=1).describe().transpose().drop(["count"], axis=1)

  #maintenance overall stats
  stats["Maint"] = pd.concat(stats["Maint"], ignore_index = True)
  m1 = stats["Maint"].drop(["sim_id"], axis=1).rename(columns={"Duration":"value"})
  m1["Measure"] = "Duration"
  m2 = stats["Maint"].groupby(["Task","sim_id"]).count().reset_index().drop(["sim_id"], axis=1).rename(columns = {"Duration":"value"})
  m2["Measure"] = "Task Count"
  stats["Maint_Stats"] = pd.concat([m1,m2],ignore_index=True).groupby(["Task","Measure"]).describe()
  stats["Maint_Stats"].columns = stats["Maint_Stats"].columns.droplevel(0)
  
  stats["Maint"] = stats["Maint"].groupby(["Task", "sim_id"]).describe()
  stats["Maint"].columns = stats["Maint"].columns.map('_'.join)
  stats["Maint"].rename(columns={"Duration_count":"Count"}, inplace=True)

  processed_timestamp = datetime.now()

  result = {}
  result["times"] = {"Start": str(start_timestamp),
                    "Model Compilation":str(compiled_timestamp - start_timestamp),
                    "Model Simulation": str(simulated_timestamp - compiled_timestamp),
                    "Results Processing":str(processed_timestamp - simulated_timestamp),
                    "Finish": str(processed_timestamp)}
  result["details"] = details
  result["stats"] = stats

  return result
    
 

#final function option 2
def run_ram_model_pool(equipmentdf, subsystemdf, systemdf, failuremodedf, inspectiondf, tbmdf, cbmdf, failuremoderesponsesdf, inventorydf, componentlistdf, duration,n_sims):

  start_timestamp = datetime.now()
  #compile model and receive result
  compiled_model = compile_ram_model(equipmentdf, subsystemdf, systemdf, failuremodedf,
                                     inspectiondf, tbmdf, cbmdf, failuremoderesponsesdf)

  hierarchydf = compiled_model["hierarchy"]
  eq_fm_map = compiled_model["eq_fm_map"]
  failuremodedf = compiled_model["failuremodedf"]
  inspectiondf = compiled_model["inspectiondf"]
  tbmdf = compiled_model["tbmdf"]
  cbmdf = compiled_model["cbmdf"]
  failuremoderesponsesdf = compiled_model["failuremoderesponsesdf"]
  compiled_timestamp = datetime.now()

  details = []
  #use pool
  with Pool(processes=4, initializer=grh.helper_init_seed) as pool:
    all_sims = [
      pool.apply_async(run_rcm_simulation,
                       [failuremodedf, inspectiondf, tbmdf, cbmdf, inventorydf,
                         failuremoderesponsesdf, componentlistdf, duration])
      for i in range(n_sims)
    ]

    for sim in all_sims:
      sim_result = sim.get(timeout=None)
      details.append(sim_result)
  
  simulated_timestamp = datetime.now()

  stats = []

  
  for d in details:
    #process result
    stats.append(None)

  processed_timestamp = datetime.now()
  result = {}
  result["times"] = {"Start":str(start_timestamp),
                    "Model Compilation":str(compiled_timestamp - start_timestamp),
                    "Model Simulation": str(simulated_timestamp - compiled_timestamp),
                    "Results Processing":str(processed_timestamp - simulated_timestamp)}
  result["details"] = details
  result["stats"] = stats

  return result




#final function option 3
def run_ram_model_celery(self, request_form, meta):
  
  #retrieve the model from the database
  meta["status"] = "Loading Model & Compiling Model"
  meta["total"] = 2
  meta["current"] = 0
  self.update_state(meta = meta)
  model = ram_db_functions.helper_query_ram_model_db_by_model_id(modelid=request_form['model_id'],format="df")
  equipmentdf = model["equipment"]
  subsystemdf=model["subsystemstructure"]
  systemdf=model["system"]
  failuremodedf=model["failuremodes"]
  inspectiondf=None
  tbmdf = None
  cbmdf = model["conditionbasedmaintenance"]
  failuremoderesponsesdf=model["equipmentfailuremoderesponses"]
  inventorydf = model["inventory"]
  componentlistdf = model["componentlistdetails"]
  duration = float(request_form['dur'])
  n_sims = int(request_form['n_sims'])

  meta["current"] = 1
  self.update_state(meta = meta)

  model_result = run_ram_model(equipmentdf,
                               subsystemdf,
                               systemdf,
                               failuremodedf,
                               inspectiondf,
                               tbmdf,
                               cbmdf,
                               failuremoderesponsesdf,
                               inventorydf,
                               componentlistdf,
                               duration,
                               n_sims,
                               updates = [self,meta])


        

  result = {}
  result["times"] = gff.helper_dict_to_std_html(model_result["times"], "times")

  for k,v in model_result["stats"].items():
    result[k] = gff.helper_format_df_as_std_html(v)
    
  #result["av"] = gff.helper_format_df_as_std_html(model_result["stats"]["Sys_Av"])
  #result["inv"] = gff.helper_format_df_as_std_html(model_result["stats"]["Inv_Av"])
  #result["eq_av"] = gff.helper_format_df_as_std_html(model_result["stats"]["Eq_Av"])
  #result["av_stats"] = gff.helper_format_df_as_std_html(model_result["stats"]["Sys_Av_Stats"])
  #result["inv_stats"] = gff.helper_format_df_as_std_html(model_result["stats"]["Inv_Av_Stats"])
  #result["eq_av_stats"] = gff.helper_format_df_as_std_html(model_result["stats"]["Eq_Av_Stats"])
  #result["eq_crit"] = gff.helper_format_df_as_std_html(model_result["stats"]["Eq_Crit"], ff= '{:,.2%}'.format)
  #result["eq_crit_stats"] = gff.helper_format_df_as_std_html(model_result["stats"]["Eq_Crit_Stats"])
  result["n_sims"] = n_sims

  #plots
  #reloth.histogram(model_result["stats"]["Sys_Av"]["uptime_%"].to_list())
  plt.hist(model_result["stats"]["Sys_Av"]["uptime_%"], edgecolor = "black")
  img = gff.helper_save_curr_plt_as_byte()
  prod_plot = gff.helper_save_byte_as_image_tag(img)
  result["plots"] = {"production_plot":prod_plot}

  #convert to json serialisable for celery task passing
  for d in model_result["details"]:
    for k, v in d.items():
      try:
        d[k] = v.to_json()
      except:
        d[k] = v
  
  result["details"] = model_result["details"]

  for k,v in model_result["stats"].items():
    try:
      model_result["stats"][k] = v.to_json()
    except:
      model_result["stats"][k] = v
        
  result["stats"] = model_result["stats"]


  
  return result



#helper for returning results from a single ram model run
def return_model_results_by_sim_id(compiled_results, sim_id):

  #access sim details for event logs and lifetimes to chart
  sim_id = int(sim_id)
  sim_index = sim_id - 1 # zero based
  
  result = {} #initialise return dict

  sim_details = compiled_results["details"][sim_index]
  result["uptime_plt"] = grh.helper_plot_time_based_df_as_html_image(pd.read_json(sim_details["FM_lifetimes"]))
  result["inv_plt"] = grh.helper_plot_time_based_df_as_html_image(pd.read_json(sim_details["inventory_lifetimes"]))
  result["ev_log"] = gff.helper_format_df_as_std_html(pd.read_json(sim_details["Event_log_all"]))
  result["m_log"] = gff.helper_format_df_as_std_html(pd.read_json(sim_details["Maintenance_log_all"]))

  #access sim stats and filter by sim id
  stats = compiled_results["stats"]
  for k in ["Sys_Av","Eq_Av","Inv","Eq_Crit"]:
    df = pd.read_json(stats[k])
    print(df)
    result[k] = gff.helper_format_df_as_std_html(df.loc[df.sim_id==sim_id])

  return result
  