
from app import create_app
import pandas as pd
from app.extensions import ramsuitedb as db

#load models
from app.models.ram import ram_model_index, ram_model_equipment, ram_model_equipment, ram_model_subsystem_index, ram_model_subsystem_structure, ram_model_system_structure, ram_model_inventory, ram_model_equipment_failure_modes, ram_model_component_list_index, ram_model_component_list_details, ram_model_condition_based_maintenance, ram_model_equipment_failure_mode_responses

from app.models.maintenance import fmea_index, fmea_function, fmea_functional_failure

Flask_app, celery = create_app()

def init_ram_tables():
  with Flask_app.app_context():
   #db.Table("ram_model_index").drop(db.engine)
    tbls = ["ram_model_index",
            "ram_model_equipment",
            "ram_model_subsystem_index",
            "ram_model_subsystem_structure",
            "ram_model_system_structure",
            "ram_model_inventory",
            "ram_model_equipment_failure_modes",
            "ram_model_component_list_index",
            "ram_model_component_list_details",
            "ram_model_condition_based_maintenance",
            "ram_model_equipment_failure_mode_responses"]
    for tbl in tbls:
      try:
        db.Table(tbl).drop(db.engine)
      except:
        pass
    #db.drop_all()
    
    db.create_all()
    
    #Add example data
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
   #db.Table("ram_model_index").drop(db.engine)
    tbls = ["fmea_index",
           "fmea_function",
           "fmea_functional_failure"]
    for tbl in tbls:
      try:
        db.Table(tbl).drop(db.engine)
      except:
        pass
    #db.drop_all()
    db.create_all()

    from app.maintenance.static.helpers.fmea_examples import fmea_examples
    fmeas = fmea_examples()

    for fmea in fmeas:
      fmea_doc = fmea_index(**fmea["meta"])

      for function in fmea["functions"]:
        func = fmea_function(**function["meta"])

        for functional_failure in function["functional_failure"]:
          fail = fmea_functional_failure(**functional_failure)

          func.functional_failures.append(fail)

        fmea_doc.functions.append(func)

      db.session.add(fmea_doc)

    db.session.commit()
      
  return

#inits to run
init_fmea_tables()