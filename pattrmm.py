import os
import time
import argparse
import importlib
import pkgutil
import schedule
import cores


# Arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--run",
    action="store_true",
    help="Run immediately."
)
parser.add_argument(
    "--times",
    type=str,
    help="Comma-separated times to run, e.g., '02:00,04:30'"
)
args = parser.parse_args()


def load_cores():
    # Core discovery
    loaded_cores = []

    for module_info in sorted(
        pkgutil.iter_modules(cores.__path__),
        key=lambda x: x.name
    ):
        module_name = module_info.name

        if module_name.startswith("_"):
            continue

        module = importlib.import_module(
            f"{cores.__name__}.{module_name}"
        )

        if hasattr(module, "run"):
            loaded_cores.append(module)

    return loaded_cores


def pattrmm():
    start_time = time.time()

    for core in load_cores():
        core_name = core.__name__.split(".")[-1]
        print(f"Running core: {core_name}")
        core.run()

    total_elapsed_time = time.time() - start_time
    total_minutes = int(total_elapsed_time // 60)
    total_seconds = int(total_elapsed_time % 60)

    message = (
        f"All operations complete. "
        f"Run time {total_minutes:02}:{total_seconds:02}"
    )

    print(message)


def get_run_times():
    times = (
        args.times
        if args.times
        else os.getenv("PATTRMM_TIMES", "02:00")
    )

    return [
        run_time.strip()
        for run_time in times.split(",")
        if run_time.strip()
    ]


run_times = get_run_times()


# Run immediately
if args.run or os.getenv("RUN_NOW", "false").lower() == "true":
    print("Running immediately...")
    pattrmm()


# Schedule
else:
    for run_time in run_times:
        schedule.every().day.at(run_time).do(pattrmm)

    display_times = []

    for run_time in run_times:
        dtime_24hour = time.strptime(run_time, "%H:%M")
        display_times.append(time.strftime("%I:%M %p", dtime_24hour))

    print(f"Waiting for the next run at: {', '.join(display_times)}")

    while True:
        schedule.run_pending()
        time.sleep(1)
