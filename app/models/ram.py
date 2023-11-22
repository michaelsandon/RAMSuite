from app.extensions import ramsuitedb as db
from sqlalchemy import func

#model index
class ram_model_index(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  desc = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())
  equipment = db.relationship("ram_model_equipment", backref='model', lazy=True)
  subsystems = db.relationship("ram_model_subsystem_index", backref='model', lazy=True)
  systemblocks = db.relationship("ram_model_system_structure", backref='model', lazy=True)
  inventory = db.relationship("ram_model_inventory", backref='model', lazy=True)
  componentlists = db.relationship("ram_model_component_list_index", backref='model', lazy=True)
  cbmtasks = db.relationship("ram_model_condition_based_maintenance", backref='model', lazy=True)

  def __repr__(self):
      return f'<Ram Model {self.title}>'

#equipment
class ram_model_equipment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  modelid = db.Column(db.Integer, db.ForeignKey('ram_model_index.id'), nullable=False)
  tag = db.Column(db.String(100), nullable=False)
  capacity = db.Column(db.Text, nullable=True)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())
  failuremodes = db.relationship("ram_model_equipment_failure_modes", backref='equipment', lazy=True)

  def __repr__(self):
      return f'<Equipment: Model {self.modelid} Tag {self.tag}>'

#subsystems
class ram_model_subsystem_index(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  modelid = db.Column(db.Integer, db.ForeignKey('ram_model_index.id'), nullable=False)
  tag = db.Column(db.String(100), nullable=False)
  capacity = db.Column(db.Text, nullable=True)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())
  ss_structure = db.relationship("ram_model_subsystem_structure", backref='ss_parent', lazy=True)

  def __repr__(self):
      return f'<Subsystem: Model {self.modelid} Equipment {self.tag}>'

#subsystem details
class ram_model_subsystem_structure(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  subsystemid = db.Column(db.Integer, db.ForeignKey('ram_model_subsystem_index.id'), nullable=False)
  tag = db.Column(db.String(100), nullable=False)
  type = db.Column(db.String(100), nullable=False)
  level = db.Column(db.Integer, nullable=False)
  m = db.Column(db.Integer, nullable=True)
  n = db.Column(db.Integer, nullable=True)
  refid = db.Column(db.Integer, nullable=True)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())

  def __repr__(self):
      return f'<Subsystem block: Subsystem {self.subsystemid} Block {self.tag}>'

#system
class ram_model_system_structure(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  modelid = db.Column(db.Integer, db.ForeignKey('ram_model_index.id'), nullable=False)
  tag = db.Column(db.String(100), nullable=False)
  type = db.Column(db.String(100), nullable=False)
  level = db.Column(db.Integer, nullable=False)
  m = db.Column(db.Integer, nullable=True)
  n = db.Column(db.Integer, nullable=True)
  refid = db.Column(db.Integer, nullable=True)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())

  def __repr__(self):
      return f'<System block: System {self.modelid} Block {self.tag}>'

#equipment failure modes
class ram_model_equipment_failure_modes(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  equipmentid = db.Column(db.Integer, db.ForeignKey('ram_model_equipment.id'), nullable=False)
  desc = db.Column(db.String(100), nullable=False)
  tbf_dist = db.Column(db.Text, nullable=False)
  tbf_par1 = db.Column(db.Double, nullable=False)
  tbf_par2 = db.Column(db.Double, nullable=True)
  tbf_par3 = db.Column(db.Double, nullable=True)
  ttd_dist = db.Column(db.Text, nullable=False)
  ttd_par1 = db.Column(db.Double,db.ColumnDefault("Const"), nullable=False)
  ttd_par2 = db.Column(db.Double, nullable=True)
  ttd_par3 = db.Column(db.Double, nullable=True)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())
  #responses = db.relationship("ram_model_equipment_failure_mode_responses", foreign_keys="failuremodeid")#, #backref='equipment', lazy=True)

  def __repr__(self):
      return f'<FailureMode: Model {self.equipment.model.id} Equipment {self.equipment.tag} Failure Mode {self.id}>'

#equipment failure auto responses
class ram_model_equipment_failure_mode_responses(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  failuremodeid = db.Column(db.Integer, db.ForeignKey('ram_model_equipment_failure_modes.id'), nullable=False)
  optional_desc = db.Column(db.String(100), nullable=True)
  cbmid = db.Column(db.Integer, db.ForeignKey('ram_model_condition_based_maintenance.id'), nullable=True)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())
  failuremode = db.relationship("ram_model_equipment_failure_modes", foreign_keys=[failuremodeid], backref="responses")
  cbmtask = db.relationship("ram_model_condition_based_maintenance", foreign_keys=[cbmid])


  def __repr__(self):
      return f'<FailureMode Auto Response: FM {self.failuremodeid} Response {self.id}>'

#inventory
class ram_model_inventory(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  modelid = db.Column(db.Integer, db.ForeignKey('ram_model_index.id'), nullable=False)
  desc = db.Column(db.String(100), nullable=False)
  min_lvl = db.Column(db.Integer, nullable=False)
  max_lvl = db.Column(db.Integer, nullable=False)
  leadtime = db.Column(db.Double, nullable=True)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())

  def __repr__(self):
      return f'<Material: Model {self.modelid} Material {self.desc}>'


#cbm tasks
class ram_model_condition_based_maintenance(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  modelid = db.Column(db.Integer, db.ForeignKey('ram_model_index.id'), nullable=False)
  desc = db.Column(db.String(100), nullable=False)
  target_fm = db.Column(db.Integer, db.ForeignKey('ram_model_equipment_failure_modes.id'), nullable=False)
  active_maint_time = db.Column(db.Double, nullable=False)
  availability_after_maint = db.Column(db.Double, nullable=False)
  availability_after_maintenance_is_abs = db.Column(db.Boolean, nullable=False)
  virtual_life_after_maint = db.Column(db.Double, nullable=False)
  virtual_life_after_maint_is_abs = db.Column(db.Boolean, nullable=False)
  executed_offline = db.Column(db.Boolean, nullable=False)
  isdp_req = db.Column(db.Boolean, nullable=False)
  component_list_id = db.Column(db.Integer, db.ForeignKey('ram_model_component_list_index.id'), nullable=True)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())

  def __repr__(self):
      return f'<CBM task: Model {self.modelid} Desc {self.desc}>'

#component lists
class ram_model_component_list_index(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  modelid = db.Column(db.Integer, db.ForeignKey('ram_model_index.id'), nullable=False)
  desc = db.Column(db.String(100), nullable=False)
  created_at = db.Column(db.DateTime(timezone=True),
     server_default=func.now())
  components = db.relationship("ram_model_component_list_details", backref='list', lazy=True)
  cbm = db.relationship("ram_model_condition_based_maintenance", backref='list', lazy=True)

  def __repr__(self):
      return f'<component list: Model {self.modelid} Id {self.id}>'

#component lists
class ram_model_component_list_details(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  listid = db.Column(db.Integer, db.ForeignKey('ram_model_component_list_index.id'), nullable=False)
  materialid = db.Column(db.Integer, db.ForeignKey('ram_model_inventory.id'), nullable=False)
  qty = db.Column(db.Integer, nullable=False)
  created_at = db.Column(db.DateTime(timezone=True),
     server_default=func.now())

  def __repr__(self):
      return f'<component list: Model {self.modelid} Id {self.id}>'