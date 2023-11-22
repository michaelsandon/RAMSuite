from flask import Flask
from config import Config
from app.static.helpers.site_map import site_map
from app.extensions import celery, ramsuitedb


def create_app(config_class=Config, standalone = False):
  app = Flask(__name__)
  app.config.from_object(config_class)

  # Initialize Flask extensions here
  ## redis for task management
  if standalone:
    from redis import Redis
    redis = Redis(host='localhost', port=6379)

  ##celery
  #celery = make_celery(app)
  celery.conf.update(app.config["CELERY_CONFIG"])
  celery.set_default()

  ##ramdb
  ramsuitedb.init_app(app)
  
  # Global vars
  @app.context_processor
  def navbar():
    return dict(site_map=site_map)

  # Register blueprints here
  from app.main import bp as main_bp
  app.register_blueprint(main_bp)

  from app.tasks import bp as task_bp
  app.register_blueprint(task_bp, url_prefix='/tasks')

  from app.survival import bp as survival_bp
  app.register_blueprint(survival_bp, url_prefix='/survival')

  from app.availability import bp as availability_bp
  app.register_blueprint(availability_bp, url_prefix='/availability')

  from app.maintenance import bp as maintenance_bp
  app.register_blueprint(maintenance_bp, url_prefix='/maintenance')

  from app.examples import bp as example_bp
  app.register_blueprint(example_bp, url_prefix='/examples')

  from app.resources import bp as resources_bp
  app.register_blueprint(resources_bp, url_prefix='/resources')


  # main driver function
  if standalone:
    return app, celery, redis
  else:
    return app, celery



