redis-server & 
python3 run.py & 
celery -A run.celery worker -P threads --loglevel=DEBUG -n worker1@%h