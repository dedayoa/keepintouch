'''
Created on Aug 10, 2016

@author: Dayo
'''

import subprocess
from sys import stdout

if __name__ == "__main__":
        
    proc1 = subprocess.run('python manage.py rqworker default sms email', shell=True, stdout = stdout)
    proc2 = subprocess.run('python manage.py rqscheduler', shell=True, stdout = stdout)