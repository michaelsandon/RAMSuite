from flask import Flask
from config import Config
from app.static.helpers.main_data import site_map
from app.extensions import make_celery, ramdb
from redis import Redis

def create_app(config_class=Config):
  app = Flask(__name__)
  app.config.from_object(config_class)

  # Initialize Flask extensions here
  ## redis for task management
  redis = Redis(host='localhost', port=6379)

  ##celery
  celery = make_celery(app)
  celery.set_default()

  ##
  ramdb.init_app(app)
  


  # Global vars
  @app.context_processor
  def navbar():
    return dict(site_map=site_map)

  # Register blueprints here
  from app.main import bp as main_bp
  app.register_blueprint(main_bp)

  from app.survival import bp as survival_bp
  app.register_blueprint(survival_bp, url_prefix='/survival')

  from app.availability import bp as availability_bp
  app.register_blueprint(availability_bp, url_prefix='/availability')

  from app.tasks import bp as task_bp
  app.register_blueprint(task_bp)
  # main driver function

  return app, celery, redis, ramdb



