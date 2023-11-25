from app.extensions import ramsuitedb as db
from sqlalchemy import func
from .dbgenerics import *

#FMEA index
class fmea_index(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  desc = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())
  functions = db.relationship("fmea_function", backref='fmea_index', lazy=True)
  failuremodes  = db.relationship("fmea_failure_mode", backref='fmea_index', lazy=True)
  failuremap = db.relationship("fmea_failure_map", backref='fmea_index', lazy=True)
  def __repr__(self):
      return f'<FMEA document {self.title}>'


class fmea_function(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  fmeaId = db.Column(db.Integer, db.ForeignKey('fmea_index.id'), nullable=False)
  desc = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime(timezone=True),
     server_default=func.now())
  functional_failures = db.relationship("fmea_functional_failure", backref='function', lazy=True)

  def __repr__(self):
    return f'<FMEA function {self.desc}>'

class fmea_functional_failure(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  fmeaFunctionId = db.Column(db.Integer, db.ForeignKey('fmea_function.id'), nullable=False)
  desc = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime(timezone=True),
     server_default=func.now())
  consequences = db.relationship("fmea_functional_failure_consequence", backref='functional_failure', lazy=True)

  def __repr__(self):
    return f'<FMEA functional failure {self.id}>'

class fmea_functional_failure_consequence(db.Model):
  id = dbpk()
  fmeaFunctionFailureId = dbfk('fmea_functional_failure.id')
  riskCategoryId = dbfk('risk_matrix_risk_category.id')
  riskConsequenceId = dbfk('risk_matrix_consequence.id')
  desc = dbstring(500,True)
  created_at = db.Column(db.DateTime(timezone=True),
     server_default=func.now())

  def __repr__(self):
    return f'<FMEA functional failure consequence {self.id}>'

class fmea_failure_mode(db.Model):
  id = dbpk()
  fmeaId = dbfk('fmea_index.id', nullable=False)
  riskLikelihoodId = dbfk('risk_matrix_likelihood.id')
  component = dbstring()
  damage = dbstring()
  mechanism = dbstring()
  longdesc = db.column_property("Component:" + component + '<br>' + "Damage:" + damage + '<br>' + "Mechanism:" + mechanism)
  created_at = dbcreated()

  def __repr__(self):
    return f'<FMEA failure mode {self.longdesc}>'


class fmea_failure_map(db.Model):
  id = dbpk()
  fmeaId = dbfk('fmea_index.id')
  fmeaFunctionalFailureId = dbfk('fmea_functional_failure.id')
  fmeaFailureModeId = dbfk('fmea_failure_mode.id')
  created_at = dbcreated()

  def __repr__(self):
    return f'<FMEA failure map {self.id}>'
  
  
  