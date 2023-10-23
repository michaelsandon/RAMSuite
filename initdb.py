#from flask import Flask
#from flask_sqlalchemy import SQLAlchemy
from app import create_app
#import os
import pandas as pd

#Method 1 to Set up database connection
#basedir = os.path.abspath(os.path.dirname(__file__))
# create the extension
#ramdb = SQLAlchemy()
# create the app
#Flask_app = Flask(__name__)
# configure the SQLite database, relative to the app instance folder
#Flask_app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'app.db')
# initialize the app with the extension
#ramdb.init_app(Flask_app)


#Method 2 to set up db connection
Flask_app, celery, redis, ramdb = create_app()

with Flask_app.app_context():
  #test that connection is successful
  #print(ramdb)

  #load and delete current db tables
  #ramdb.reflect()
  #for t in ramdb.metadata.tables.values():
    #print(t.name)
    #t.drop(ramdb.engine)
  ramdb.drop_all()
  #ramdb.metadata.clear()


  #load models & create tables
  from app.models.ram import ram_model_index
  from app.models.ram import ram_model_equipment
  from app.models.ram import ram_model_subsystem_index
  from app.models.ram import ram_model_subsystem_structure
  from app.models.ram import ram_model_system_structure
  from app.models.ram import ram_model_inventory
  from app.models.ram import ram_model_equipment_failure_modes
  from app.models.ram import ram_model_component_list_index
  from app.models.ram import ram_model_component_list_details
  from app.models.ram import ram_model_condition_based_maintenance
  from app.models.ram import ram_model_equipment_failure_mode_responses
  ramdb.create_all()
  
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
    ramdb.session.add(model)
    ramdb.session.flush()
    
    #add subsystems and subsystem-structures
    for subsys in sys["sub-systems"]:
      ss = ram_model_subsystem_index(tag=subsys["tag"], modelid=model.id)
      ramdb.session.add(ss)
      ramdb.session.flush()
      
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

        ramdb.session.add(block)
        ramdb.session.flush()

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

      ramdb.session.add(block)

    #add inventory
    for matl in sys["inventory"]:
      matl["modelid"]=model.id
      ramdb.session.add(ram_model_inventory(**matl))
    ramdb.session.flush()

    #add material lists
    for matl_list in sys["material_lists"]:
      material_list = ram_model_component_list_index(modelid = model.id, desc = matl_list["desc"])
      for comps in matl_list["materials"]:
        material_list.components.append(ram_model_component_list_details(**comps))
      ramdb.session.add(material_list)
    ramdb.session.flush()
    
    #add cbm tasks
    fms_s = ramdb.select(ram_model_equipment_failure_modes).join(ram_model_equipment).join(ram_model_index).where(ram_model_index.id==model.id).order_by(ram_model_equipment.id)
    fms = ramdb.session.execute(fms_s).scalars().all()
    for cbm_task in sys["maintenance_cbm"]:
      if cbm_task["component_list_id"] is not None:
        cbm_task["component_list_id"] = model.componentlists[cbm_task["component_list_id"]-1].id
      cbm_task["modelid"]=model.id
      cbm_task["target_fm"] = fms[cbm_task["target_fm"]-1].id
      ramdb.session.add(ram_model_condition_based_maintenance(**cbm_task))
    ramdb.session.flush()
    
    #add failure mode responses on failure
    counter = 0
    for eq in sys["equipment"]:
      for fm in eq["fm"]:
        counter = counter+1
        for resp in fm["responses_on_failure"]["cbm"]:
          #cbm is not empty list
          ramdb.session.add(ram_model_equipment_failure_mode_responses(failuremodeid = fms[counter-1].id, cbmid = model.cbmtasks[resp-1].id))
    ramdb.session.flush()

    #
  #ramdb.session.execute(ram_model_index.__table__.insert(), model_meta)
  #ram_models = ram_model.query.all()

#  for m in ram_models:
#    print([m.title, m.desc])

  ramdb.session.commit()

