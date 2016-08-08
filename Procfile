web: gunicorn keepintouch.wsgi --log-file -
worker: python manage.py rqworker default sms email
scheduler: python manage.py rqscheduler
