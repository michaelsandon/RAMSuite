from . import maint_db_functions as maint_db_funcs


def render_fmea(fmeaid):
  tbls = maint_db_funcs.helper_query_fmea_by_id(fmeaid = fmeaid, format = 'df')

  fmea = tbls["functions"].merge(tbls["functionalfailures"])