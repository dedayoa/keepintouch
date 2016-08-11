'''
Created on Aug 10, 2016

@author: Dayo
'''

import subprocess
import time
import psutil


def kill(proc_pid):
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        proc.kill()
    process.kill()


if __name__ == "__main__":
        
    proc1 = subprocess.run('python manage.py rqworker default sms email')
    proc2 = subprocess.run('python manage.py rqscheduler')
    
    proc_list = [proc1, proc2]
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        for proc in proc_list:
            kill(proc)