import sys
sys.path.insert(0,'/home/runner/RAMSuite/')

from app import create_app
import pandas as pd
from app.extensions import ramsuitedb as db

#load models
from app.models.maintenance import fmea_index as fi, fmea_function as ff, fmea_functional_failure as fff, fmea_functional_failure_consequence as fffc, fmea_failure_map as ffmp, fmea_failure_mode as ffmd
from app.models.risk import risk_matrix_consequence as rmc, risk_matrix_risk_category as rmrc, risk_matrix_likelihood as rml, risk_matrix_risk_map as rmrm, risk_matrix_risk_level as rmrl
import pandas as pd
import app.static.helpers.global_formatting_functions as gff
import app.maintenance.static.helpers.maint_db_functions as maint_db_funcs

Flask_app = create_app()["app"]

with Flask_app.app_context():
  #res = maint_db_funcs.helper_query_combined_fmea_by_id(fmeaid=1,format="df", grouped=False)
  qry2 = db.select(ff.desc.label("Function"),
                  fff.desc.label("Functional Failure"),
                  fffc.desc.label("Consequence Description"),
                  rmrc.desc.label("Risk Category"),
                  rmc.desc.label("Consequence"),
                  rmc.index.label("clvl"),
                   fff.id.label("fffid"),
                   ffmd.id.label("ffmdid")
   ).join(fff, fff.fmeaFunctionId == ff.id).join(fffc, fffc.fmeaFunctionFailureId == fff.id, isouter=True).join(rmc, fffc.riskConsequenceId == rmc.id,isouter=True).join(rmrc, fffc.riskCategoryId == rmrc.id,isouter=True).join(ffmp, fff.id == ffmp.fmeaFunctionalFailureId, isouter=True).join(ffmd,ffmp.fmeaFailureModeId == ffmd.id, isouter=True).join(rml, ffmd.riskLikelihoodId == rml.id).join(rmrm, (rmc.index == rmrm.cindex) & (rml.index == rmrm.lindex), isouter=True).join(rmrl, rmrl.index == rmrm.rindex, isouter = True)

  conn = db.session.connection()
  res = pd.read_sql(sql=qry2,con=conn)

  res["Risk Category"].fillna("0", inplace=True)
  df1 = res.pivot(index=["Function","Functional Failure","fffid","ffmdid"], columns = ["Risk Category"],values = ["Consequence"])

  df1.drop([('Consequence','0')],axis=1,inplace=True)

  df1.columns = df1.columns.droplevel(0)
  print(df1)

  l = ["Function","Functional Failure","fffid"]
  l = l + df1.columns.to_list()
  l.append("ffmdid")
  print(l)

df2 = df1.reset_index()
df2["spare"] = "spare"
df2["spare2"] = "spare"

df2 = df2.pivot(index = l,columns = ["spare"],values=["spare2"])
print(df2)
