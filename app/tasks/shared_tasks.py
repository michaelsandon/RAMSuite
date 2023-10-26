from celery import shared_task
from app.availability.static.helpers.availability_functions import package_uptime_celery
from app.availability.static.helpers.ram_functions import run_ram_model_celery

### refactored celery tasks to route through a common task manager
@shared_task(bind=True, acks_late = True)
def celery_task_router(self,request_form,dest,url_to_render):
  #print("test")
  meta = {'current': 0,
          'total': 1,
          'status': "Started"
          }
  
  if dest == "av-pu":
    result = package_uptime_celery(self,request_form=request_form, meta = meta)
  elif dest == "av-ram":
    result = run_ram_model_celery(self, request_form=request_form, meta=meta)
  return result

def helper_update_celery_task_state(task_obj, base_meta, meta_field, meta_value):
  meta = base_meta
  meta[meta_field] = meta_value
  task_obj.update_state(state = "PROGRESS",meta=meta)
