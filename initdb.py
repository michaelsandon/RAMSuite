from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import create_app
import os

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
  ramdb.reflect()
  #for t in ramdb.metadata.tables.values():
    #print(t.name)
    #t.drop(ramdb.engine)
  ramdb.drop_all()
  ramdb.metadata.clear()


  #load models & create tables
  from app.models.ram import ram_model_index
  from app.models.ram import ram_model_equipment
  from app.models.ram import ram_model_subsystem_index
  from app.models.ram import ram_model_subsystem_structure
  ramdb.create_all()
  
  #Add example data
  ##ram examples
  import app.availability.static.helpers.ram_functions as ram_funcs
  RAM_examples = ram_funcs.rbd_examples()
  model_meta = []
  for sys in RAM_examples["deconstructed"].values():
    #create Ram model object
    model = ram_model_index(**sys["meta"])

    #prepare equipment
    for equip in sys["equipment"]:
      model.equipment.append(ram_model_equipment(**equip["meta"]))

    #add subsystems and subsystem-structures
    for subsys in sys["sub-systems"]:
      ss = ram_model_subsystem_index(tag=subsys["tag"])
      for subsysblock in subsys["structure"]:
        if subsysblock["type"] == "Equipment":
          block = ram_model_subsystem_structure(tag = subsysblock["tag"],
                                                type = subsysblock["type"],
                                                level = subsysblock["level"],
                                                refid = model.equipment[subsysblock["localid"]-1].id
                                               )
        elif subsysblock["type"] == "Subsystem":
          block = ram_model_subsystem_structure(tag = subsysblock["tag"],
                                                type = subsysblock["type"],
                                                level = subsysblock["level"],
                                                refid = model.subsystems[subsysblock["localid"]-1].id
                                               )
        else:
          block = ram_model_subsystem_structure(**subsysblock)

        ss.ss_structure.append(block)

      model.subsystems.append(ss)

    #add equipment and model in one
    ramdb.session.add(model)

    #refresh db to have unique ids available
    #ramdb.flush()


      
  
  #ramdb.session.execute(ram_model_index.__table__.insert(), model_meta)
  #ram_models = ram_model.query.all()

#  for m in ram_models:
#    print([m.title, m.desc])

  ramdb.session.commit()
