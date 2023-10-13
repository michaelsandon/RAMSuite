from app.extensions import ramdb as db
from sqlalchemy import func

class ram_model_index(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  desc = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())
  equipment = db.relationship("ram_model_equipment", backref='model', lazy=True)
  subsystems = db.relationship("ram_model_subsystem_index", backref='model', lazy=True)
  systemblocks = db.relationship("ram_model_system_structure", backref='model', lazy=True)

  def __repr__(self):
      return f'<Ram Model {self.title}>'

class ram_model_equipment(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  modelid = db.Column(db.Integer, db.ForeignKey('ram_model_index.id'), nullable=False)
  tag = db.Column(db.String(100), nullable=False)
  capacity = db.Column(db.Text, nullable=True)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())

  def __repr__(self):
      return f'<Equipment: Model {self.modelid} Tag {self.tag}>'

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