import os
import time
import argparse

# Arguments
parser = argparse.ArgumentParser()
parser.add_argument("--run", action="store_true", help="Run immediately.")
parser.add_argument("--times", type=str, help="Comma-separated times to run, e.g., '02:00,04:30'")
args = parser.parse_args()

# Get times
run_times = args.times.split(",") if args.times else os.getenv("PATTRMM_TIMES", "02:00").split(",")
run_now = args.run or os.getenv("RUN_NOW", "false").lower() == "true"

# Run now
if run_now:
    print("Running immediately...")
    with open("pattrmm.py") as f:
        exec(f.read())

# Schedule
else:
    print(f"Waiting for the next run at: {', '.join(run_times)}")
    while True:
        current_time = time.strftime("%H:%M")
        
        if current_time in run_times:
            print(f"Starting {current_time} run...")
            with open("pattrmm.py") as f:
                exec(f.read())
            
            time.sleep(60)  # Wait a minute
            print(f"Waiting for the next run at: {', '.join(run_times)}")
        
        time.sleep(1)  # Check every second
