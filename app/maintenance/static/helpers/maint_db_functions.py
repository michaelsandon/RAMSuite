from app.extensions import ramsuitedb
from app.models.maintenance import fmea_index as fi, fmea_function as ff, fmea_functional_failure as fff, fmea_functional_failure_consequence as fffc, fmea_failure_map as ffmp, fmea_failure_mode as ffmd
from app.models.risk import risk_matrix_consequence as rmc, risk_matrix_risk_category as rmrc, risk_matrix_likelihood as rml, risk_matrix_risk_map as rmrm, risk_matrix_risk_level as rmrl
import pandas as pd
import app.static.helpers.global_formatting_functions as gff
from sqlalchemy import join

def colour_risk(val,colourmap):
  if val is None or pd.isna(val):
    colour = 'white'
  else:
    colour = colourmap.loc[colourmap.Risk==val,"colour"].iloc[0]
  return 'background-color: %s' % colour

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
  
  qry = db.select(ff.desc.label("Function"),
    fff.desc.label("Functional Failure"),
    fffc.desc.label("Consequence Description"),
    rmrc.desc.label("Risk Category"),
    rmc.desc.label("Consequence"),
    rmc.index.label("clvl"),
     fff.id.label("fffid"),
     ffmd.id.label("ffmdid"),
     ffmd.longdesc.label("Failure Mode"),
     rml.desc.label("Likelihood"),
     rml.index.label("llvl"),
     rmrl.desc.label("Risk"),
     rmrl.colour
  ).join(fff, fff.fmeaFunctionId == ff.id).join(fffc, fffc.fmeaFunctionFailureId == fff.id, isouter=True).join(rmc, fffc.riskConsequenceId == rmc.id,isouter=True).join(rmrc, fffc.riskCategoryId == rmrc.id,isouter=True).join(ffmp, fff.id == ffmp.fmeaFunctionalFailureId, isouter=True).join(ffmd,ffmp.fmeaFailureModeId == ffmd.id, isouter=True).join(rml, ffmd.riskLikelihoodId == rml.id).join(rmrm, (rmc.index == rmrm.cindex) & (rml.index == rmrm.lindex), isouter=True).join(rmrl, rmrl.index == rmrm.rindex, isouter = True)


  if fmeaid is not None:
    qry = qry.join(fi, fi.id == ff.fmeaId).where(fi.id == fmeaid)
    
  conn = db.session.connection()
  
  
  if format == "scalars":
    result = db.session.scalars(qry)
  elif format == "dict":
    result = pd.read_sql(sql=qry,con=conn).to_dict(orient='records')
  elif format in ["df","html","html-std"]:
    result = pd.read_sql(sql=qry,con=conn)
    colourmap = result.loc[:,["Risk","colour"]].copy().drop_duplicates()

    
    if grouped:
      #j1 establishes max consequence level
      j1 = result.loc[:,["fffid","clvl"]].copy()
      j1 = j1.groupby("fffid").max().reset_index()
      j1 = j1.merge(result.loc[:,["Consequence","clvl"]].drop_duplicates(),on='clvl',how='left') #.drop(["clvl"],axis=1)

      #j2 establishes pivoted consequences
      j2 = result.loc[:,["fffid","Risk Category","Consequence"]].copy().drop_duplicates()
      j2["Risk Category"].fillna("0", inplace=True)
      j2 = j2.pivot(index = "fffid",columns = ["Risk Category"],values = ["Consequence"])
      try:
        j2.drop([('Consequence','0')],axis=1,inplace=True)
      except:
        pass
      j2.columns = j2.columns.droplevel(0)
      riskcats = j2.columns.to_list()
      j2.reset_index(inplace=True)

      #j3 establish consequence description
      j3 = result.loc[:,["fffid","Risk Category","Consequence Description"]].copy().drop_duplicates()
      j3["Consequence Description"] = j3.apply(lambda x: '' if pd.isna(x["Risk Category"]) else ('<b>'+x["Risk Category"] + '</b>: <br>' + x["Consequence Description"]), axis=1)
      j3 = j3.groupby(['fffid'])['Consequence Description'].apply(lambda x: '<br>'.join(x)).reset_index()

      #j4
      j4 = result.loc[:,["llvl","Risk","clvl"]].copy().drop_duplicates()

      #final query
      f = result.drop(["Consequence Description","Risk Category", "Consequence","clvl","Risk","colour"], axis=1).merge(j1, on = 'fffid', how = 'left').merge(j2, on = 'fffid', how = 'left').merge(j3, on = 'fffid', how = 'left').merge(j4, on = ["clvl","llvl"], how = 'left')
      f.drop_duplicates(inplace=True)

      #final pivot
      fp = f.copy()
      fp["spare"] = "spare"
      fp["spare2"] = ""
      fp = fp.pivot(index = ["Function","Functional Failure","Consequence Description"]+riskcats+["Consequence","Failure Mode","Likelihood","Risk"],columns = ["spare"],values=["spare2"])
      fp.columns = fp.columns.droplevel(0)
      fp.reset_index(level=["Risk"], inplace=True)
      fp.drop(["spare"],axis=1,inplace=True)

      result = fp


      #consider if you can drop all columns from and add to index and only leave index
    
    
    if format == "html":
      result = result.style.map(colour_risk,colourmap =colourmap,subset=["Risk"]).to_html()
      result = gff.helper_reformat_grouped_df_html(result)
    elif format == "html-std":
      result = gff.helper_format_df_as_std_html(result.style.map(colour_risk,colourmap =colourmap,subset=["Risk"]))
      result = gff.helper_reformat_grouped_df_html(result)

  return result