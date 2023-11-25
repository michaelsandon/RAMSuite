from app.extensions import ramsuitedb as db
from sqlalchemy import func

#generic primary key
def dbpk():
  return db.Column(db.Integer, primary_key=True)

#integer
def dbinteger(nullable = False):
  return db.Column(db.Integer, nullable=nullable)

#foreignkey
def dbfk(fk,nullable = False):
  return db.Column(db.Integer, db.ForeignKey(fk), nullable=nullable)

#string
def dbstring(length = 100, nullable = False):
  return db.Column(db.String(length), nullable=nullable)

#created
def dbcreated():
  return db.Column(db.DateTime(timezone=True),server_default=func.now())