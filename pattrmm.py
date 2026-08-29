import os
import time
import argparse
import subprocess
import sys
import importlib
import pkgutil
import schedule


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

parser.add_argument(
    "--settings",
    type=str,
    help="Comma-separated settings files to run."
)

parser.add_argument(
    "--run-single",
    action="store_true",
    help=argparse.SUPPRESS
)

args = parser.parse_args()


def get_settings_files():
    settings_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "settings"
    )

    settings = (
        args.settings
        if args.settings
        else os.getenv("PATTRMM_SETTINGS")
    )

    if settings:
        return [
            settings_file.strip()
            for settings_file in settings.split(",")
            if settings_file.strip()
        ]

    return sorted(
        file
        for file in os.listdir(settings_dir)
        if file.endswith((".yml", ".yaml"))
    )


def load_cores():
    import cores

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

        print(
            f"Running core: {core_name}"
        )

        core.run()

    total_elapsed_time = time.time() - start_time
    total_minutes = int(total_elapsed_time // 60)
    total_seconds = int(total_elapsed_time % 60)

    print(
        f"All operations complete. "
        f"Run time {total_minutes:02}:{total_seconds:02}"
    )


def run_all_settings():
    start_time = time.time()

    settings_files = get_settings_files()

    print(
        f"Found {len(settings_files)} settings file(s): "
        f"{', '.join(settings_files)}"
    )

    for settings_file in settings_files:

        print()
        print("=" * 60)
        print(
            f"Running settings: {settings_file}"
        )
        print("=" * 60)

        env = os.environ.copy()
        env["PATTRMM_SETTINGS"] = settings_file

        result = subprocess.run(
            [
                sys.executable,
                os.path.abspath(__file__),
                "--run-single"
            ],
            env=env
        )

        if result.returncode != 0:
            print(
                f"Settings file {settings_file} "
                f"failed with exit code "
                f"{result.returncode}"
            )

    total_elapsed_time = time.time() - start_time
    total_minutes = int(total_elapsed_time // 60)
    total_seconds = int(total_elapsed_time % 60)

    print()
    print(
        f"All settings complete. "
        f"Total run time {total_minutes:02}:{total_seconds:02}"
    )


def get_run_times():
    times = (
        args.times
        if args.times
        else os.getenv(
            "PATTRMM_TIMES",
            "02:00"
        )
    )

    return [
        run_time.strip()
        for run_time in times.split(",")
        if run_time.strip()
    ]


run_times = get_run_times()


# Run a single settings file.
# This is used internally by run_all_settings().
if args.run_single:

    settings_file = os.getenv(
        "PATTRMM_SETTINGS",
        "settings.yml"
    )

    print(
        f"Using settings: {settings_file}"
    )

    pattrmm()


# Run selected/all settings immediately.
elif (
    args.run
    or os.getenv(
        "RUN_NOW",
        "false"
    ).lower() == "true"
):

    print("Running settings...")
    run_all_settings()


# Schedule
else:

    for run_time in run_times:
        schedule.every().day.at(
            run_time
        ).do(run_all_settings)

    display_times = []

    for run_time in run_times:
        dtime_24hour = time.strptime(
            run_time,
            "%H:%M"
        )

        display_times.append(
            time.strftime(
                "%I:%M %p",
                dtime_24hour
            )
        )

    print(
        f"Waiting for the next run at: "
        f"{', '.join(display_times)}"
    )

    while True:
        schedule.run_pending()
        time.sleep(1)
