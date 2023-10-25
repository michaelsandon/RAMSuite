import sys
sys.path.insert(0,'/home/runner/RAMSuite/')

from app import create_app

Flask_app, celery, redis, ramdb = create_app()

testid = 4
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
  duration = 300000

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
  
    print(test_result["FM_lifetimes"])
    print(test_result["Event_log_all"])

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
                                 n_sims=10)

    print(model_result["times"])
    
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

