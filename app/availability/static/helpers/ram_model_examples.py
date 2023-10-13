import pandas as pd

#helper function for initialising compiled rbds which can be fed directly to the rbd plotting functions
def new_rbd(SystemName = "System", Systemtype = "System - Series", description = "", m = None, n = None):
  d = {'tag': SystemName,
      'description': description,
      'level':1,
      'type':Systemtype,
      'm':m,
      'n':n}
  result = pd.DataFrame(data=d,  index=[1])
  return result


#helper function for initialising compiled rbds
def add_rbd_block(RBD = new_rbd(), tag = "", description = "", level = 2, type = "Equipment", m = None, n = None):
  new_row = {'tag': tag,
      'description': description,
      'level':level,
      'type':type,
      'm':m,
      'n':n}
  
  RBD.loc[len(RBD)+1] = new_row
  
  result = RBD
  
  return result











#helperfunction for initialising deconstructed models
def new_model(title, desc, type="System - Series"):
  model = {"meta":{"title":title,"desc":desc},
          "equipment":[],
          "sub-systems":[],
          "system":[],
          "maintenance_cbm":[],
          "inventory":[],
          }
  return model

#helperfunction for init decon equip
def new_equipment(eq_tag, eq_cap=0):
  equipment = {"meta":{"tag":eq_tag, "capacity":eq_cap},
               "fm":[]}
  return equipment

#helperfunction for modifying model eq
def add_eq_to_model(model,eq):
  model["equipment"].append(eq)
  return model

#helperfunction for init fm
def new_fm(fm_desc,tbe_dist,tbe_par1,ttd_dist,ttd_par1,tbe_par2=None,tbe_par3=None,ttd_par2=None,ttd_par3=None,resp_cbm=[]):
  fm = {"desc":fm_desc,
        "tbe":{'dist': tbe_dist,'par1': tbe_par1,'par2': tbe_par2,'par3': tbe_par3},
        "ttd":{'dist': ttd_dist,'par1': ttd_par1,'par2': ttd_par2,'par3': ttd_par3},
        "responses_on_failure":{"cbm":resp_cbm} #selected from cbm tasks
        }
  return fm

#helperfunction for modifying model eq fms
def add_fm_to_eq(eq,fm):
  eq["fm"].append(fm)
  return eq

def new_subsys(ss_tag,type="System - Series",m=None,n=None):
  ss = {"tag":ss_tag,"structure":[new_block(block_tag=ss_tag,type = type, level = 1,m=m,n=n)]}
  return ss

def add_subsys_to_model(model,ss):
  model["sub-systems"].append(ss)
  return model

def new_block(block_tag,type="Equipment",level=2,localid=None,m=None,n=None):
  block = {"tag":block_tag,"type":type,"level":level,"localid":localid,"m":m,"n":n}
  return block
  
def add_block_to_subsys(ss,block):
  ss["structure"].append(block)
  return ss

def add_block_to_sys(model,block):
  model["system"].append(block)
  return model

def new_material(material_desc,min_level=0,max_level=5,lead_time=8760):
  matl = {"desc":material_desc,"min":min_level,"max":max_level,"leadtime":lead_time}
  return matl

def add_matl_to_inventory(model,matl):
  model["inventory"].append(matl)
  return model

def new_tbm_maint_task(desc,target_fm,actvmt,aam_val,vlam_val,aam_is_abs=True,vlam_is_abs=True,on_or_off="off",tbc=8760):
  #actvmt = active_maint_time
  #aam = availabiltiy after maintenance val = value(double),r_or_a = relative or absolute
  #vlam = virtual life after maintenance
  #on_or_off = online or offline
  #tbc = time between calls in hours e.g. every 24 hrs, weekly (24*7)
  mt = {"desc":desc, "target_fm":target_fm, "active_maint_time":actvmt, "availability_after_maint":aam_val, "availability_after_maintenance_is_abs":aam_is_abs,"virtual_life_after_maint":vlam_val,"virtual_life_after_maint_is_abs":vlam_is_abs, "online_or_offline":on_or_off, "time_between_calls":tbc,"materials":[]}
  return mt

def new_cbm_maint_task(desc,target_fm,actvmt,aam_val,vlam_val,aam_is_abs=True,vlam_is_abs=True,on_or_off="off",isdp_req=False):
  #actvmt = active_maint_time
  #aam = availabiltiy after maintenance
  #vlam = virtual life after maintenance
  #on_or_off = online or offline
  #tbc = time between calls in hours e.g. every 24 hrs, weekly (24*7)
  mt = {"desc":desc, "target_fm":target_fm, "active_maint_time":actvmt, "availability_after_maint":aam_val, "availability_after_maintenance_is_abs":aam_is_abs,"virtual_life_after_maint":vlam_val,"virtual_life_after_maint_is_abs":vlam_is_abs, "online_or_offline":on_or_off, "isdp_req":isdp_req,"materials":[]}
  return mt

def new_component_req(matlid,qty):
  req = {"material":matlid,"qty":qty}
  return req

def add_matl_req_to_maint_task(task,req):
  task["materials"].append(req)
  return task


#function to develop a compiled rbd of a firewater system
def fw_compiled_rbd():
  df = new_rbd("Firewater System")
  df = add_rbd_block(RBD = df, tag = "Pump System", level = 2, type = "System - Parallel", m = 1, n = 2)
  df = add_rbd_block(RBD = df, tag = "Pump Package 1", level = 3, type = "System - Series")
  df = add_rbd_block(RBD = df, tag = "Pump 1", level = 4, type = "Equipment")
  df = add_rbd_block(RBD = df, tag = "motor 1", level = 4, type = "Equipment")
  df = add_rbd_block(RBD = df, tag = "Pump Package 2", level = 3, type = "System - Series")
  df = add_rbd_block(RBD = df, tag = "Pump 2", level = 4, type = "Equipment")
  df = add_rbd_block(RBD = df, tag = "motor 2", level = 4, type = "Equipment")
  df = add_rbd_block(RBD = df, tag = "Pump Package 3", level = 3, type = "System - Series")
  df = add_rbd_block(RBD = df, tag = "Pump 3", level = 4, type = "Equipment")
  df = add_rbd_block(RBD = df, tag = "motor 3", level = 4, type = "Equipment")
  df = add_rbd_block(RBD = df, tag = "Ringmain", level = 2, type = "Equipment")
  df = add_rbd_block(RBD = df, tag = "Nozzles", level = 2, type = "Equipment")
  
  return df

#function to develop a compiled rbd of a instrument loop system
def il_compiled_rbd():
  df = new_rbd("Basic Instrument Loop")
  df = add_rbd_block(RBD = df, tag = "Sensor")
  df = add_rbd_block(RBD = df, tag = "Controller")
  df = add_rbd_block(RBD = df, tag = "Control Valve")
  return df

#function to develop a compiled rbd of a pump system
def pumps_compiled_rbd():
  df = new_rbd("Pumps in Parallel", Systemtype = "System - Parallel", m = 2, n = 3)
  df = add_rbd_block(RBD = df, tag = "Pump 1")
  df = add_rbd_block(RBD = df, tag = "Pump 2")
  df = add_rbd_block(RBD = df, tag = "Pump 3")
  return df  

#function to build a dict object to house a fw model for ram modelling. To be used by database init script
def fw_decon_ram():
  #create model
  model = new_model(title="Firewater", desc="Firewater system - pumps and spray sections")

  #create equipment
  model = add_eq_to_model(model = model, eq = new_equipment(eq_tag="Nozzles"))
  model = add_eq_to_model(model = model, eq = new_equipment(eq_tag="Ringmain"))
  
  #create fms for pumps before adding them
  pump = new_equipment(eq_tag="Pump")
  pump = add_fm_to_eq(eq = pump, fm = new_fm(fm_desc="pump impeller failure",tbe_dist= "Weibull_Distribution", tbe_par1=2*8760,
                                             tbe_par2= 2, ttd_dist="const",ttd_par1= 1,resp_cbm=[1]))
  model = add_eq_to_model(model = model, eq=pump)

  #create fms for motor
  motor = new_equipment(eq_tag="Motor")
  motor = add_fm_to_eq(eq = motor, fm = new_fm(fm_desc="motor winding failure",tbe_dist= "Weibull_Distribution", tbe_par1=10*8760,
                                               tbe_par2= 1.4, ttd_dist="const",ttd_par1= 1,resp_cbm=[2]))
  model = add_eq_to_model(model = model, eq=motor)

  #create subsystems
  ss1 = new_subsys(ss_tag="Pump Package")
  ss1 = add_block_to_subsys(ss = ss1,block = new_block(block_tag="Pump",localid=3))
  ss1 = add_block_to_subsys(ss = ss1,block = new_block(block_tag="Motor",localid=4))

  ss2 = new_subsys(ss_tag="Pump System", type = "System - Parallel",m=1,n=2)
  ss2 = add_block_to_subsys(ss = ss2,block = new_block(block_tag="Pump Package",type="Subsystem",localid=1))
  ss2 = add_block_to_subsys(ss = ss2,block = new_block(block_tag="Pump Package",type="Subsystem",localid=1))

  model = add_subsys_to_model(model= model, ss = ss1)
  model = add_subsys_to_model(model= model, ss = ss2)

  #create system structure
  model = add_block_to_sys(model,new_block(block_tag = "Firewater System",type="System - Series",level=1))
  model = add_block_to_sys(model,new_block(block_tag = "Pumps System",type="Subsystem",localid=2))
  model = add_block_to_sys(model,new_block(block_tag = "Ringmain",localid=2))
  model = add_block_to_sys(model,new_block(block_tag = "Nozzles",localid=1))

  #create inventory
  model = add_matl_to_inventory(model,new_material(matl_tag="Pump Assembly",min_level=1,max_level=2,lead_time=4380))
  model = add_matl_to_inventory(model,new_material(matl_tag="Pump Motor",min_level=1,max_level=2,lead_time=8760))

  #create maintenance tasks and add to model
  tsk1 = new_cbm_maint_task(desc = "Replace Pump", target_fm=1, actvmt=30,aam=1,vlam=0)
  tsk1 = add_matl_req_to_maint_task(task=tsk1, req = new_component_req(matlid=1,qty=1))
  tsk2 = new_cbm_maint_task(desc = "Replace Motor", target_fm=1, actvmt=24,aam=1,vlam=0)
  tsk2 = add_matl_req_to_maint_task(task=tsk2, req = new_component_req(matlid=2,qty=1))
  model = add_task_to_model(model,tsk1)
  model = add_task_to_model(model,tsk2)
  
  return model


#function for generating ram examples
def rbd_examples():

  decon_stabs = {
               "meta":{
                 "title":"condensate stabilisation system",
                 "desc":"5 train stabilisation system"},
               "equipment":[],
               "sub-systems":[],
               "system":[]}
  
  result = {"compiled": {"firewater" : fw_compiled_rbd(),
                        "Instrument Loop" : il_compiled_rbd(),
                        "Pump System" : pumps_compiled_rbd()},
           "deconstructed": {
             "firewater":fw_decon_ram(),
             "stabilisation":decon_stabs 
           }}
  
  return(result)
