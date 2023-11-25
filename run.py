from app import create_app

Flask_app = create_app()["app"]
#Flask_app, celery, ramdb, redis = create_app(standalone = True)

Flask_app.app_context().push()

if __name__ == "__main__":
  Flask_app.run(host='0.0.0.0', debug=True)