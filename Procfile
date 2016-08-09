web: gunicorn keepintouch.wsgi --log-file -
worker: python manage.py rqworker default sms email
clock: python manage.py rqscheduler
