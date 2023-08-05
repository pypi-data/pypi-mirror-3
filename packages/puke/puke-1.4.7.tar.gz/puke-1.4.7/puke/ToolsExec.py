import os, sys

import subprocess
import signal
from puke.Console import *
from puke.Std import *



class Alarm(Exception):
    pass

def alarm_handler(signum, frame):
    raise Alarm


def sh (command, header = None, output = True, timeout = None, std = None):
    if isinstance(command, list):
        command = " ; ".join(command)



    if header == None:
        header = 'exec "%s" ' % command
    else:
        console.debug(command)
    
    if output and header != False:
        console.header(' - '+header)


    stdErrMarker = "XXXERRORXXX"
    
    result = ""

    if timeout:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.alarm(timeout)  # 5 seconds
    

    try:
        command = "export PYTHONIOENCODING=utf-8;" + command
        cProcess = subprocess.Popen(command, stdout = subprocess.PIPE, shell = True, stderr= subprocess.PIPE, executable='/bin/bash', env=os.environ)
        (rStdout, rStderr) = cProcess.communicate()
        signal.alarm(0)
    except Alarm:
        console.debug('taking too long (%s)' % command)
        cProcess.kill()
        rStdout = rStderr = ''
    
    if std and isinstance(std, Std):
        std.set(rStdout, rStderr)

    rStdout = "%s\n%s\n%s" % (rStdout if rStdout else '', stdErrMarker if rStderr else '', rStderr if rStderr else '')

    lines = rStdout.split('\n')
    for line in lines:
        if not line:
            continue

        if output == True and stdErrMarker in line:
            console.error("")
            console.error('Std error :')
            line = ""
        

        result += line
        
        if not line.endswith('\n'):
            result += '\n'

        if output == True:
            console.info( '   ' +line)
   
    return result