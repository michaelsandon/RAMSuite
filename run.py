#from app.__init__ import create_app
from app import create_app
#from app import celery

#celery = celery
Flask_app, celery, redis, ramdb = create_app()
#Flask_app = create_app()
Flask_app.app_context().push()

if __name__ == "__main__":
  Flask_app.run(host='0.0.0.0', debug=True)