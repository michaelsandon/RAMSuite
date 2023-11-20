#redis-server & 
python3 run.py & 
celery -A run.celery worker --concurrency=4 --loglevel=DEBUG -n worker1@%h
#celery -A run.celery worker -P threads --loglevel=DEBUG -n worker1@%h