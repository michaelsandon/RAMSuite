import os
import ssl

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
  SECRET_KEY = os.environ.get('SECRET_KEY')
  MPLBACKEND = "Agg"
  CELERY_CONFIG={
    'broker_url': os.environ['CELERY_BROKER_URL'],#'redis://localhost:6379',
    'result_backend': os.environ['CELERY_RESULT_BACKEND'], #'redis://localhost:6379',
    'task_acks_late': True,
    'result_extended': True,
    'broker_use_ssl':{"ssl_cert_reqs": ssl.CERT_NONE}, #added for external redis
    'redis_backend_use_ssl':{"ssl_cert_reqs": ssl.CERT_NONE}, #added for external redis
  }
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
    or 'sqlite:///' + os.path.join(basedir, 'app.db')
  SQLALCHEMY_TRACK_MODIFICATIONS = False


#    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
#        or 'sqlite:///' + os.path.join(basedir, 'app.db')
#    SQLALCHEMY_TRACK_MODIFICATIONS = False
