from app import create_app
import pandas as pd
from app.extensions import ramsuitedb as db
import inspect

import app.models.ram as ram
import app.models.maintenance as maint
import app.models.risk as risk

#load models
from app.models.ram import *
from app.models.maintenance import *
from app.models.risk import *

import app.maintenance.static.helpers.maint_db_functions as maint_db_funcs




Flask_app = create_app()["app"]

def init_ram_tables():
  with Flask_app.app_context():
   #db.Table("ram_model_index").drop(db.engine)
    tbls = list_tbls_from_model(ram)

    drop_create_tbls(db,tbls)
    ##ram examples
    import app.availability.static.helpers.ram_model_examples as rme
    RAM_examples = rme.rbd_examples()
    model_meta = []
    for sys in RAM_examples["deconstructed"].values():
      #create Ram model object
      model = ram_model_index(**sys["meta"])
  
      #prepare equipment
      for equip in sys["equipment"]:
        eq = ram_model_equipment(**equip["meta"])
        for fm in equip["fm"]:
          fm_copy = fm.copy()
          del fm_copy["responses_on_failure"]
          fm_copy = pd.json_normalize(fm_copy, sep='_').to_dict(orient='records')[0]
          eq.failuremodes.append(ram_model_equipment_failure_modes(**fm_copy))
        model.equipment.append(eq)
  
      #add equipment and model in one
      db.session.add(model)
      db.session.flush()
      
      #add subsystems and subsystem-structures
      for subsys in sys["sub-systems"]:
        ss = ram_model_subsystem_index(tag=subsys["tag"], modelid=model.id)
        db.session.add(ss)
        db.session.flush()
        
        for subsysblock in subsys["structure"]:
          if subsysblock["type"] == "Equipment":
            block = ram_model_subsystem_structure(tag = subsysblock["tag"],
                                                  type = subsysblock["type"],
                                                  level = subsysblock["level"],
                                                  refid = model.equipment[subsysblock["localid"]-1].id,
                                                  subsystemid = ss.id
                                                 )
          elif subsysblock["type"] == "Subsystem":
            block = ram_model_subsystem_structure(tag = subsysblock["tag"],
                                                  type = subsysblock["type"],
                                                  level = subsysblock["level"],
                                                  refid = model.subsystems[subsysblock["localid"]-1].id,
                                                  subsystemid = ss.id
                                                 )
          else:
            del subsysblock["localid"]
            subsysblock["subsystemid"] = ss.id
            
            block = ram_model_subsystem_structure(**subsysblock)
  
          db.session.add(block)
          db.session.flush()
  
      #add system structure
      for systemblock in sys["system"]:
        if systemblock["type"] == "Equipment":
          block = ram_model_system_structure(tag = systemblock["tag"],
                                              type = systemblock["type"],
                                              level = systemblock["level"],
                                              refid = model.equipment[systemblock["localid"]-1].id,
                                              modelid = model.id
                                              )
        elif systemblock["type"] == "Subsystem":
          block = ram_model_system_structure(tag = systemblock["tag"],
                                              type = systemblock["type"],
                                              level = systemblock["level"],
                                              refid = model.subsystems[systemblock["localid"]-1].id,
                                              modelid = model.id
                                             )
        else:
          systemblock["modelid"] = model.id
          del systemblock["localid"]
          block = ram_model_system_structure(**systemblock)
  
        db.session.add(block)
  
      #add inventory
      for matl in sys["inventory"]:
        matl["modelid"]=model.id
        db.session.add(ram_model_inventory(**matl))
      db.session.flush()
  
      #add material lists
      for matl_list in sys["material_lists"]:
        material_list = ram_model_component_list_index(modelid = model.id, desc = matl_list["desc"])
        for comps in matl_list["materials"]:
          material_list.components.append(ram_model_component_list_details(**comps))
        db.session.add(material_list)
      db.session.flush()
      
      #add cbm tasks
      fms_s = db.select(ram_model_equipment_failure_modes).join(ram_model_equipment).join(ram_model_index).where(ram_model_index.id==model.id).order_by(ram_model_equipment.id)
      fms = db.session.execute(fms_s).scalars().all()
      for cbm_task in sys["maintenance_cbm"]:
        if cbm_task["component_list_id"] is not None:
          cbm_task["component_list_id"] = model.componentlists[cbm_task["component_list_id"]-1].id
        cbm_task["modelid"]=model.id
        cbm_task["target_fm"] = fms[cbm_task["target_fm"]-1].id
        db.session.add(ram_model_condition_based_maintenance(**cbm_task))
      db.session.flush()
      
      #add failure mode responses on failure
      counter = 0
      for eq in sys["equipment"]:
        for fm in eq["fm"]:
          counter = counter+1
          for resp in fm["responses_on_failure"]["cbm"]:
            #cbm is not empty list
            db.session.add(ram_model_equipment_failure_mode_responses(failuremodeid = fms[counter-1].id, cbmid = model.cbmtasks[resp-1].id))
      db.session.flush()
  
      #
    #db.session.execute(ram_model_index.__table__.insert(), model_meta)
    #ram_models = ram_model.query.all()
  
  #  for m in ram_models:
  #    print([m.title, m.desc])
  
    db.session.commit()

  return
  

def init_fmea_tables():
  with Flask_app.app_context():
    tbls = list_tbls_from_model(maint)
    drop_create_tbls(db,tbls)

    from app.maintenance.static.helpers.fmea_examples import fmea_examples
    fmeas = fmea_examples()

    for fmea in fmeas:
      fmea_doc = fmea_index(**fmea["meta"])

      for function in fmea["functions"]:
        func = fmea_function(**function["meta"])

        for functional_failure in function["functional_failure"]:
          fail = fmea_functional_failure(**functional_failure["meta"])

          for consequence in functional_failure["consequences"]:
            cons = fmea_functional_failure_consequence(**consequence)
            fail.consequences.append(cons)

          func.functional_failures.append(fail)

        fmea_doc.functions.append(func)


      for failuremode in fmea["failuremodes"]:
        fmode = fmea_failure_mode(**failuremode)
        fmea_doc.failuremodes.append(fmode)
        
      db.session.add(fmea_doc)
      db.session.flush()

      ffs = maint_db_funcs.helper_query_fmea_by_id(db,["functionalfailures"],fmea_doc.id,"df")
      #print(ffs)
      for mapitem in fmea["failuremap"]:
        #print(int(ffs.loc[mapitem["ref_funcfailid"]-1,"id"]))
        mi = fmea_failure_map(fmeaId = fmea_doc.id,
                              fmeaFunctionalFailureId = int(ffs.loc[mapitem["ref_funcfailid"]-1,"id"]),
                              fmeaFailureModeId = fmea_doc.failuremodes[mapitem["ref_failid"]-1].id)
        db.session.add(mi)
      

    db.session.commit()
      
  return



#init risk tables
def init_risk_tables():
  with Flask_app.app_context():
    tbls = list_tbls_from_model(risk)
    drop_create_tbls(db,tbls)
  
    from app.risk.static.helpers.risk_matrix_example import basic_matrix
    risk_matrix = basic_matrix()

    rm = risk_matrix_index(**risk_matrix["meta"])
  
    for lhood in risk_matrix["likelihoods"]:
      rm.likelihoods.append(risk_matrix_likelihood(**lhood))

    for cons in risk_matrix["consequences"]:
      rm.consequences.append(risk_matrix_consequence(**cons))

    for lvl in risk_matrix["levels"]:
      rm.levels.append(risk_matrix_risk_level(**lvl))

    for map_obj in risk_matrix["map"]:
      rm.map.append(risk_matrix_risk_map(**map_obj))

    for cat in risk_matrix["categories"]:
      rm.categories.append(risk_matrix_risk_category(**cat))
  
    db.session.add(rm)
  
    db.session.commit()

  return


def drop_create_tbls(db,tbls):
  for tbl in tbls:
    try:
      db.Table(tbl).drop(db.engine)
    except:
      pass
  db.create_all()
  return None

#helper to minimise writing all model names
def list_tbls_from_model(model):
  tbl_names = []
  for name, obj in inspect.getmembers(model):
      if inspect.isclass(obj):
        tbl_names.append(name)

  return tbl_names


##inits to run
inits = ["fmea"] #"ram","fmea","risk"
for init in inits:
  match init:
    case "ram":
      init_ram_tables()
    case "fmea":
      init_fmea_tables()
    case "risk":
      init_risk_tables()
