# Import required modules
import os
import argparse
import time
import logging  # Import logging module for logging functionality
from modules.cores import example

# Define command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--run", action="store_true")
args = parser.parse_args()

def pattrmm():
    start_time = time.time()

    # Execute the 'example.run()' function
    example.run()

    # Calculate elapsed time and convert it to minutes and seconds
    total_elapsed_time = time.time() - start_time
    total_minutes = int(total_elapsed_time // 60)
    total_seconds = int(total_elapsed_time % 60)

    # Print and log the total runtime
    print(f"All operations complete. Run time {total_minutes:02}:{total_seconds:02}")
    logging.info(f"All operations complete. Run time {total_minutes:02}:{total_seconds:02}")

# Check if the '--run' argument is provided via command-line
if args.run:
    pattrmm()
else:
    if "PATTRMM_TIME" in os.environ:
        runwhen = os.environ["PATTRMM_TIME"]
    else:
        runwhen = "02:00"
    
    dtime_24hour = time.strptime(runwhen, "%H:%M")
    dtime_12hour = time.strftime("%I:%M %p", dtime_24hour)

    print("Waiting for next run at " + str(dtime_12hour))
    
    # Infinite loop to continuously check the time and run 'pattrmm()' accordingly
    while True:
        if runwhen == time.strftime('%H:%M'):
            pattrmm()
            time.sleep(60)  # This sleep might need adjustment based on your requirements
            print("Waiting for next run at " + str(dtime_12hour))
        time.sleep(.5)
