from multiprocessing import Process
import time
import sys

import stress

MAXUSERS = 100

def usage():
    print ("Usage: multiUser <number of concurrent users> <ramp up time> <delay>")
    exit()

if (__name__ == '__main__'):
    if (len(sys.argv) < 4):
        usage()

    try:
        numUsers = int(sys.argv[1])
        rampUpTime = float(sys.argv[2])
        delay = float(sys.argv[3])
    except ValueError as err:
        print(err)
        usage()
    if (numUsers<1 or numUsers>MAXUSERS):
        usage()
    for i in range(numUsers):
        print("Lanzando el proceso " + str(i))
        p = Process(target=stress.mainLoop, args=(delay, ))
        p.start()
        time.sleep(rampUpTime)

    

