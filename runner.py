'''
Created on Aug 10, 2016

@author: Dayo
'''

import subprocess

if __name__ == "__main__":
        
    proc1 = subprocess.run('python manage.py rqworker default sms email')
    proc2 = subprocess.run('python manage.py rqscheduler')