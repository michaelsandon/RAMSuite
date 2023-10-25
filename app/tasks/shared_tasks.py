from celery import shared_task
from app.availability.static.helpers.availability_functions import post_package_uptime_v2

### refactored celery tasks to route through a common task manager
@shared_task(bind=True, acks_late = True)
def celery_task_router(self,request_form,dest):
  #print("test")
  if dest == "av-pu":
    result = post_package_uptime_v2(self,request_form=request_form)
  return result