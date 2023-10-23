from app.extensions import ramdb
from app.models.ram import ram_model_index as rmi
from app.models.ram import ram_model_equipment as rme
from app.models.ram import ram_model_subsystem_index as rmsi
from app.models.ram import ram_model_subsystem_structure as rmss
from app.models.ram import ram_model_system_structure as rms
from app.models.ram import ram_model_inventory as rminv
from app.models.ram import ram_model_equipment_failure_modes as rmfm
from app.models.ram import ram_model_component_list_index as rmcli
from app.models.ram import ram_model_component_list_details as rmcld
from app.models.ram import ram_model_condition_based_maintenance as rmcbm
from app.models.ram import ram_model_equipment_failure_mode_responses as rmfmr
import pandas as pd
import app.static.helpers.global_formatting_functions as gff


def helper_query_ram_model_db_by_model_id(db=ramdb,tables=None,modelid=None,format="dict"):

  queries = {
    "model": db.select(rmi),
    "equipment": db.select(rme).join(rmi),
    "subsystemindex": db.select(rmsi).join(rmi),
    "subsystemstructure": db.select(rmss).join(rmsi).join(rmi),
    "system": db.select(rms).join(rmi),
    "inventory": db.select(rminv).join(rmi),
    "failuremodes": db.select(rmfm).join(rme).join(rmi),
    "componentlistindex": db.select(rmcli).join(rmi),
    "componentlistdetails": db.select(rmcld).join(rmcli).join(rmi),
    "conditionbasedmaintenance": db.select(rmcbm).join(rmi),
    "equipmentfailuremoderesponses": db.select(rmfmr).join(rmfm).join(rme).join(rmi)
  }

  #return all tables if keys is None
  if tables is None:
    tables = list(queries.keys())

  #dict if format is none
  if format is None:
    format="dict"
    
  #join where filter is modelid is provided
  if modelid is not None:
    for k,v in queries.items():
      queries[k]=v.where(rmi.id==modelid)
  
  result = {}

  conn = db.session.connection()
  
  for tbl in tables:
    if format == "scalars":
      result[tbl] = db.session.scalars(queries[tbl])
    elif format == "df":
      result[tbl] = pd.read_sql(sql=queries[tbl],con=conn)
    elif format == "html":
      result[tbl] = pd.read_sql(sql=queries[tbl],con=conn).to_html()
    elif format == "html-std":
      df = pd.read_sql(sql=queries[tbl],con=conn)
      result[tbl] = gff.helper_format_df_as_std_html(df)
    elif format == "dict":
      result[tbl] = pd.read_sql(sql=queries[tbl],con=conn).to_dict(orient='records')

  #if there is only one result
  if len(tables)==1:
    result = result[tables[0]] 
    

  return result