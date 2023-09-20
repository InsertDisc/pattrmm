import time
import argparse
import os
parser = argparse.ArgumentParser()
parser.add_argument("--run", action="store_true")
parser.parse_args()
args = parser.parse_args()

if args.run == True:
    with open("pattrmm.py") as f:
        exec(f.read())


else:
    if "PATTRMM_TIME" in os.environ:
        runwhen = os.environ["PATTRMM_TIME"]
    else:
        runwhen = "02:00"
    t = 1
    
    dtime_24hour = time.strptime(runwhen, "%H:%M")
    dtime_12hour = time.strftime( "%I:%M %p", dtime_24hour )

    print("Waiting for next run at " + str(dtime_12hour))
    while t:
        if runwhen == time.strftime('%H:%M'):
            with open("pattrmm.py") as f:
                exec(f.read())
                time.sleep(60)
                print("Waiting for next run at " + str(dtime_12hour))
        time.sleep(.5)

