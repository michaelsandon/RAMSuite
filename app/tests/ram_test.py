import sys
sys.path.insert(0,'/home/runner/RAMSuite/')

import pandas as pd

from app import create_app

Flask_app, celery, redis, ramdb = create_app()

testid = 3
with Flask_app.app_context():
  import app.availability.static.helpers.ram_db_functions as ramdbfuncs

  fw_model = ramdbfuncs.helper_query_ram_model_db_by_model_id(modelid=1, format="df")

  equipmentdf = fw_model["equipment"]
  subsystemdf=fw_model["subsystemstructure"]
  systemdf=fw_model["system"]
  failuremodedf=fw_model["failuremodes"]
  inspectiondf=None
  tbmdf = None
  cbmdf = fw_model["conditionbasedmaintenance"]
  failuremoderesponsesdf=fw_model["equipmentfailuremoderesponses"]
  inventorydf = fw_model["inventory"]
  componentlistdf = fw_model["componentlistdetails"]
  duration = 150000
  

  #rcm simulation test
  if testid == 1:
    from app.availability.static.helpers.ram_functions import run_rcm_simulation
    test_result = run_rcm_simulation(failuremodedf = failuremodedf,
                                     inspectiondf=inspectiondf,
                                     tbmdf = tbmdf,
                                     cbmdf = cbmdf,
                                     inventorydf=inventorydf,
                                     failuremoderesponsesdf=failuremoderesponsesdf,
                                     componentlistdf = componentlistdf,
                                     duration=duration)
  
    #print(test_result["FM_lifetimes"])
    #print(test_result["Event_log_all"])
    print(test_result["inventory_log"])

  #ram model compilation test
  elif testid == 2:
    from app.availability.static.helpers.ram_functions import compile_ram_model
    cm = compile_ram_model(equipmentdf = fw_model["equipment"],
                           subsystemdf=fw_model["subsystemstructure"],
                           systemdf=fw_model["system"],
                           failuremodedf=fw_model["failuremodes"],
                          inspectiondf=None,
                          tbmdf = None,
                          cbmdf = fw_model["conditionbasedmaintenance"],
                          failuremoderesponsesdf=fw_model["equipmentfailuremoderesponses"])

    print(cm["hierarchy"])
    print(cm["eq_fm_map"])
    print(cm["failuremodedf"])
    print(cm["tag_map"])


  elif testid == 3:
    from app.availability.static.helpers.ram_functions import run_ram_model
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
                                 n_sims=2)

    #print(model_result["times"])
    #print(model_result["details"][0])
    print(model_result["stats"]["Inv_Stats"])
    #print(model_result["stats"]["Maint_Stats"])
    #print(model_result["stats"]["Maint"])
    #print(model_result["stats"]["Eq_Av"])
    #print(model_result["stats"]["Eq_Av_Stats"].reset_index())
    #print(model_result["stats"]["Eq_Av_Stats"])
    #print(model_result["stats"]["Sys_Av"])
    #print(model_result["stats"]["Eq_Crit"])  
    #print(model_result["stats"]["Eq_Crit_Stats"])  
    #print(model_result["details"][0])
    #m = model_result["stats"]["Maint"]
    #print(m)
    #m1 = m.drop(["sim_id"], axis=1).groupby(["Task"]).describe().drop([("Duration","count")], axis=1)
    #m1.columns = m1.columns.map('_'.join)
    #print(m1)

    #m1 = m.drop(["sim_id"], axis=1).rename(columns={"Duration":"value"})
    #m1["Measure"] = "Duration"

    #m2 = m.groupby(["Task","sim_id"]).count().reset_index().drop(["sim_id"], axis=1).rename(columns = {"Duration":"Task_Count"}).groupby(["Task"]).describe()
    #print(m2)
    #m2 = m.groupby(["Task","sim_id"]).count().reset_index().drop(["sim_id"], axis=1).rename(columns = {"Duration":"value"})
    #m2["Measure"] = "Task Count"

    #m4 = pd.concat([m1,m2], ignore_index=True).groupby(["Task","Measure"]).describe()
    #print(m4)

    #m3 = m.groupby(["Task", "sim_id"]).describe()
    #print(m3)
    
  elif testid == 4:
    from app.availability.static.helpers.ram_functions import run_ram_model, run_ram_model_pool
    model_result = run_ram_model_pool(equipmentdf,
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
                                 n_sims=10)

    print(model_result["times"])

  debug = None

