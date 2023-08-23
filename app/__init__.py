from flask import Flask
from config import Config
from app.main.main_data import site_map


def create_app(config_class=Config):
  app = Flask(__name__)
  app.config.from_object(config_class)

  # Initialize Flask extensions here

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
  # main driver function

  return app
