from app.extensions import ramsuitedb
from app.models.maintenance import fmea_index as fi, fmea_function as ff, fmea_functional_failure as fff, fmea_functional_failure_consequence as fffc, fmea_failure_map as ffmp, fmea_failure_mode as ffmd
from app.models.risk import risk_matrix_consequence as rmc, risk_matrix_risk_category as rmrc, risk_matrix_likelihood as rml, risk_matrix_risk_map as rmrm, risk_matrix_risk_level as rmrl
import pandas as pd
import app.static.helpers.global_formatting_functions as gff
from sqlalchemy import join


def helper_query_fmea_by_id(db=ramsuitedb,tables=None,fmeaid=None,format="dict"):

  queries = {
    "doc": db.select(fi),
    "functions": db.select(ff).join(fi),
    "functionalfailures": db.select(fff).join(ff).join(fi),
    "functionalfailureconsequences":db.select(fffc).join(fff).join(ff).join(fi)
  }

  #return all tables if keys is None
  if tables is None:
    tables = list(queries.keys())

  #dict if format is none
  if format is None:
    format="dict"

  #join where filter is modelid is provided
  if fmeaid is not None:
    for k,v in queries.items():
      queries[k]=v.where(fi.id==fmeaid)

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


def helper_query_combined_fmea_by_id(db=ramsuitedb,fmeaid=None,format="dict", grouped=True):
  
  conn = db.session.connection()

  qry1 = db.select(ff.desc.label("Function"),
                  fff.desc.label("Functional Failure"),
                  fffc.desc.label("Consequence Description"),
                  rmrc.desc.label("Risk Category"),
                  rmc.desc.label("Consequence"),
                  ffmd.longdesc.label("Failure Mode"),
                  rml.desc.label("Failure Likelihood"),
                  rmrl.desc.label("Risk")
                 ).join(fff, fff.fmeaFunctionId == ff.id).join(fffc, fffc.fmeaFunctionFailureId == fff.id, isouter=True).join(rmc, fffc.riskConsequenceId == rmc.id,isouter=True).join(rmrc, fffc.riskCategoryId == rmrc.id,isouter=True).join(ffmp, fff.id == ffmp.fmeaFunctionalFailureId, isouter=True).join(ffmd,ffmp.fmeaFailureModeId == ffmd.id, isouter=True).join(rml, ffmd.riskLikelihoodId == rml.id).join(rmrm, (rmc.index == rmrm.cindex) & (rml.index == rmrm.lindex), isouter=True).join(rmrl, rmrl.index == rmrm.rindex, isouter = True)

  qry2 = db.select(ff.desc.label("Function"),
    fff.desc.label("Functional Failure"),
    fffc.desc.label("Consequence Description"),
    rmrc.desc.label("Risk Category"),
    rmc.desc.label("Consequence"),
    ffmd.longdesc.label("Failure Mode"),
    rml.desc.label("Failure Likelihood"),
    rmrl.desc.label("Risk")
   ).join(fff, fff.fmeaFunctionId == ff.id).join(fffc, fffc.fmeaFunctionFailureId == fff.id, isouter=True).join(rmc, fffc.riskConsequenceId == rmc.id,isouter=True).join(rmrc, fffc.riskCategoryId == rmrc.id,isouter=True).join(ffmp, fff.id == ffmp.fmeaFunctionalFailureId, isouter=True).join(ffmd,ffmp.fmeaFailureModeId == ffmd.id, isouter=True).join(rml, ffmd.riskLikelihoodId == rml.id).join(rmrm, (rmc.index == rmrm.cindex) & (rml.index == rmrm.lindex), isouter=True).join(rmrl, rmrl.index == rmrm.rindex, isouter = True)
  
  if fmeaid is not None:
    qry = qry.join(fi, fi.id == ff.fmeaId).where(fi.id == fmeaid)

  
  if format == "scalars":
    result = db.session.scalars(qry)
  elif format == "dict":
    result = pd.read_sql(sql=qry,con=conn).to_dict(orient='records')
  elif format in ["df","html","html-std"]:
    result = pd.read_sql(sql=qry,con=conn)
    if grouped:
      result["blank"] = 0
      result= result.pivot(index=["Function","Functional Failure","Risk Category","Consequence Description"], columns = ["blank"],values = ["Consequence"]).droplevel(1,axis=1)
      #consider if you can drop all columns from and add to index and only leave index
    if format == "html":
      result = result.to_html()
    elif format == "html-std":
      result = gff.helper_format_df_as_std_html(result)

  return result