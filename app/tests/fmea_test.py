import sys
sys.path.insert(0,'/home/runner/RAMSuite/')

from app import create_app
import pandas as pd
from app.extensions import ramsuitedb as db
from bs4 import BeautifulSoup

#load models
from app.models.maintenance import fmea_index as fi, fmea_function as ff, fmea_functional_failure as fff, fmea_functional_failure_consequence as fffc, fmea_failure_map as ffmp, fmea_failure_mode as ffmd
from app.models.risk import risk_matrix_consequence as rmc, risk_matrix_risk_category as rmrc, risk_matrix_likelihood as rml, risk_matrix_risk_map as rmrm, risk_matrix_risk_level as rmrl
import pandas as pd
import app.static.helpers.global_formatting_functions as gff
import app.maintenance.static.helpers.maint_db_functions as maint_db_funcs

Flask_app = create_app()["app"]


with Flask_app.app_context():
  #res = maint_db_funcs.helper_query_combined_fmea_by_id(fmeaid=2,format="html-std", grouped=True)
  res = maint_db_funcs.helper_query_fmea_by_id(fmeaid=1,format="scalars")
  print(res["doc"].one().id)
  