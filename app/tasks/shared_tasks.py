from celery import shared_task
### refactored celery tasks to route through a common task manager
@shared_task(bind=True, acks_late = True)
def celery_task_router(self,request_form,dest,url_to_render):
  #forced to defer import due to circular dependencies on start up if needing to avoid this, must spit into separate task manager modules
  from app.survival.static.helpers.survival_functions import survival_analysis_celery
  from app.availability.static.helpers.availability_functions import package_uptime_celery
  from app.availability.static.helpers.ram_functions import run_ram_model_celery
  #note: url_to_render used in routes for tasks
  meta = {'current': 0,
          'total': 1,
          'status': "Started"
          }
  if dest == "surv-fit":
    result = survival_analysis_celery(self,request_form=request_form, meta = meta)
  elif dest == "av-pu":
    result = package_uptime_celery(self,request_form=request_form, meta = meta)
  elif dest == "av-ram":
    result = run_ram_model_celery(self, request_form=request_form, meta = meta)
  return result

def helper_update_celery_task_state(task_obj, base_meta, meta_field, meta_value):
  meta = base_meta
  meta[meta_field] = meta_value
  task_obj.update_state(state = "PROGRESS",meta=meta)
