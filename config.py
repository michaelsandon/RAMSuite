import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY')
  MPLBACKEND = "Agg"
  CELERY_CONFIG={
    'broker_url': 'redis://localhost:6379',
    'result_backend': 'redis://localhost:6379',
    'task_acks_late': True
  }
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
    or 'sqlite:///' + os.path.join(basedir, 'app.db')
  SQLALCHEMY_TRACK_MODIFICATIONS = False


#    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
#        or 'sqlite:///' + os.path.join(basedir, 'app.db')
#    SQLALCHEMY_TRACK_MODIFICATIONS = False
