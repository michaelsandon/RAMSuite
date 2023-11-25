from app.extensions import ramsuitedb as db
from sqlalchemy import func
from .dbgenerics import *

#RM index
class risk_matrix_index(db.Model):
  id = dbpk()
  title = dbstring()
  likelihoodrange = dbinteger()
  consequencerange = dbinteger()
  created_at = dbcreated()
  likelihoods = db.relationship("risk_matrix_likelihood", backref='matrix', lazy=True)
  consequences = db.relationship("risk_matrix_consequence", backref='matrix', lazy=True)
  levels = db.relationship("risk_matrix_risk_level", backref='matrix', lazy=True)
  map = db.relationship("risk_matrix_risk_map", backref='matrix', lazy=True)
  categories = db.relationship("risk_matrix_risk_category", backref='matrix', lazy=True)
  
  def __repr__(self):
      return f'<Risk Matrix {self.title}>'

#RM likelihood
class risk_matrix_likelihood(db.Model):
  id = dbpk()
  riskMatrixId = dbfk('risk_matrix_index.id')
  index = dbinteger()
  desc = dbstring(100,True)
  created_at = dbcreated()

  def __repr__(self):
    return f'<RM likelhood {self.id}>'

#RM consequences
class risk_matrix_consequence(db.Model):
  id = dbpk()
  riskMatrixId = dbfk('risk_matrix_index.id')
  index = dbinteger()
  desc = dbstring(100,True)
  created_at = dbcreated()

  def __repr__(self):
    return f'<RM Consequences {self.id}>'

#RM Levels
class risk_matrix_risk_level(db.Model):
  id = dbpk()
  riskMatrixId = dbfk('risk_matrix_index.id')
  index = dbinteger()
  desc = dbstring(100,False)
  colour = dbstring()
  created_at = dbcreated()

  def __repr__(self):
    return f'<RM Level {self.id}>'

#RM map
class risk_matrix_risk_map(db.Model):
  id = dbpk()
  riskMatrixId = dbfk('risk_matrix_index.id')
  lindex = dbinteger()
  cindex = dbinteger()
  rindex = dbinteger()
  created_at = dbcreated()

  def __repr__(self):
    return f'<RM map {self.id}>'

#RM Cats
class risk_matrix_risk_category(db.Model):
  id = dbpk()
  riskMatrixId = dbfk('risk_matrix_index.id')
  desc = dbstring(100,False)
  created_at = dbcreated()

  def __repr__(self):
    return f'<RM map {self.id}>'
