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
    proc_list = []
    
    commands = ["python manage.py rqworker default sms email",
               "python manage.py rqscheduler"
               ]
    for command in commands:
        print("$ "+command)
        proc = subprocess.run(command)
        proc_list.append(proc)
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        for proc in proc_list:
            kill(proc)