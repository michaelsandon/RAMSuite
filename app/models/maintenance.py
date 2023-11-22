from app.extensions import ramsuitedb as db
from sqlalchemy import func

#FMEA index
class fmea_index(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(100), nullable=False)
  desc = db.Column(db.Text, nullable=False)
  created_at = db.Column(db.DateTime(timezone=True),
                         server_default=func.now())
  functions = db.relationship("fmea_function", backref='fmea_index', lazy=True)
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

  def __repr__(self):
    return f'<FMEA functional failure {self.desc}>'