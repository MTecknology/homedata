import os
import sys
import logging
import yaml

import scandir

def run_delete(snapshot):
    with open("targets.tmp", 'r') as delete_files:
        for line in delete_files.readlines():
            file = line.split()[0]
            uid = int(line.split()[1])
            logging.debug("{} {}".format(file, uid))
            if not snapshot and ".snapshot" in file:
                logging.debug("Skipping Snapshot " + file)
                continue
            delete_fork(file, uid)

def delete_fork(file, uid):
    logging.debug("spawning fork")
    pid = os.fork()
    if pid == 0:
        try:
            set_uid_and_delete(file, uid)
        finally:
            os._exit(0)
    logging.debug("Launching Fork PID {}".format(pid))
    return (pid)

def set_uid_and_delete(file, uid):
    try:
        os.setuid(uid)
    except:
        err = sys.exc_info()[0]
        logging.debug(err)
    delete_file(file)

def delete_file(file):
    try:
        os.remove(file)
        logging.info("Deleted File: {}".format(file))
    except OSError as err:
        logging.error("Caught Exception: {}".format(err))

def load_homes():
    homes = {}
    try:
        if os.stat('delete_keys.yml').st_size > 0:
            with open('delete_keys.yml') as homesyml:
                homes = yaml.load(homesyml)
            logging.info("Yaml loaded: {} homes".format(str(len(homes))))
        else:
            logging.error("Yaml file has 0 entries")
            sys.exit(1)
    except OSError as err:
        logging.error("Caught Exception: {}".format(err))
        sys.exit(1)
    return homes

def main(snapshot):
    homes = load_homes()
    targets = True
    with open("targets.tmp", 'w') as targetfile:
        targetfile.write('')
    os.chmod('targets.tmp', 0o666)
    scandir.run_scandir(homes, targets, "delete_keys.yml")
    logging.info("Start new delete operations")
    run_delete(snapshot)

if __name__ == "__main__":
    pids = {}    # Pid lookup table to match PID with homedir (globally available)
    snapshot = False
    for arg in sys.argv:         #Populates ssh if option specified. This scans only ~/.ssh/
        if "--debug" in arg:
            loglevel = logging.DEBUG
        else:
            loglevel = logging.INFO
        if "--snapshot" in sys.argv:
            snapshot=True

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',filename='delete_keys.log',level=loglevel)
    logging.info("Start Scan")
    logging.debug("debug")
    os.chmod('delete_keys.log', 0o666) # Creates initial log file if absent, changes permission so forks can access it

    main(snapshot)
