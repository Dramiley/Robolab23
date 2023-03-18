import json
import os
import time

# DONT CHANGE ANYTHING HERE, ONLY IN .env
# Bitte nicht hierdrinne verändern, sondern in der src/.env setzen.
# siehe https://se-gitlab.inf.tu-dresden.de/robolab-spring/ws2022/group-046/-/blob/master/README.md#example-for-development-purposes
__current_dir = os.path.dirname(os.path.realpath(__file__))
env = {"SIMULATOR": False}

if os.path.exists(__current_dir + "/.env"):
    with open(__current_dir + "/.env") as f:
        print("Using .env file.")
        for line in f:
            # if line is empty, skip it
            if line == "\n":
                continue
            key, value = line.split("=")
            value = value.replace("\n", "")
            print("Setting " + key + " to " + value)
            if value == "True" or value == "False":
                env[key] = value == "True"
            else:
                env[key] = value
else:
    print("No .env file found. Using default values.")


def simulator_log(log_type, log_dict):
    if not env["SIMULATOR"]:
        return

    # set payload type
    log_dict["type"] = log_type

    # append to history file (which contains an array of positions)
    from lockfile import LockFile
    lock = LockFile(__current_dir + "/simulator/history.json.lock")
    with lock:
        time.sleep(0.001)

    lock.acquire()
    with open(__current_dir + '/simulator/history.json', 'r+') as outfile:
        try:
            data = json.load(outfile)
        except:
            data = []

        # append to array
        data.append(log_dict)

        # write to file
        outfile.seek(0)
        json.dump(data, outfile)
    lock.release()
