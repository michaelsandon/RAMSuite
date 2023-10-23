import sys
sys.path.insert(0,'/home/runner/RAMSuite/')

from app import create_app

Flask_app, celery, redis, ramdb = create_app()

with Flask_app.app_context():
  import app.availability.static.helpers.ram_db_functions as ramdbfuncs

  fw_model = ramdbfuncs.helper_query_ram_model_db_by_model_id(modelid=1, format="df")

  from app.availability.static.helpers.ram_functions import run_rcm_strategy


  test_result = run_rcm_strategy(failuremodedf = fw_model["failuremodes"],
                                 inspectiondf=None,
                                 tbmdf = None,
                                 cbmdf = fw_model["conditionbasedmaintenance"],
                                 inventorydf=fw_model["inventory"],
                                 failuremoderesponsesdf=fw_model["equipmentfailuremoderesponses"],
                                 componentlistdf = fw_model["componentlistdetails"],
                                 duration=300000)

  print(test_result["FM_lifetimes"])
  print(test_result["Event_log_all"])

  debug = None

