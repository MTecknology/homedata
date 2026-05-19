# Wrapper script for dirscan.pl. Requires Python >3.7 and pyYaml

import os
import sys
import yaml
import logging
import time
from func_timeout import func_timeout, FunctionTimedOut

def spawn_forks(home, targets=False):
    """ This creates a forked process for the UID change needed to run scanhomes """
    pid = os.fork()
    if pid == 0:
        try:
            scan_target(home, targets)
        finally:
            os._exit(0)
    logging.debug("Launching Fork PID {}".format(pid))
    return (pid)

def iterate(queue, targets=False):
    """ Used to wrap the next iteration in try except and run the spawn_forks function """
    try:
        home = next(queue)
        logging.debug("Next iteration {}".format(str(home)))
    except StopIteration:      # Returns False when reaching the last object so the caller knows to stop.
        return (False, 0, 'None')
    pid = spawn_forks(home, targets)
    return (True, pid, home)                # returns True if there's another iteration available.


def scan_target(home, targets=False):
    """ Wraps the file scanner in os.walk to recursely scan the destination(home) """
    uid = 0
    try:                          # Checks directory exists and gets UID for scan process
        stathome = os.stat(home)
        if os.path.isdir(home):
            uid = stathome.st_uid
    except OSError as err:
        logging.debug("{} {}".format(home, error ))
        return False
    logging.debug("Scan started {}, {}".format(uid, home))
    os.setuid(uid)                # Changes UID so that the directory can be read, rootsquashfs not configured
    for root, dirs, files in os.walk(home):
        for file in files:
            try:
                savetarget = func_timeout(2, scan_file, args=(root + "/" + file, targets))
            except FunctionTimedOut as err:
                logging.debug("Caught Exception: FunctionTimedOut on {}".format(root + "/" + file))
            if savetarget:
                with open("targets.tmp", 'a') as targetwrite:
                    targetwrite.write("{} {}\n".format(savetarget, uid))

def scan_file(file, targets=False):
    """ Loads the first 500 bytes and compares to Valid SSH Key headers, logs unencrypted keys """
    headers = {
        b"-----BEGIN EC PRIVATE KEY-----",   # SSH Key headers that don't imply encryption
        b"-----BEGIN RSA PRIVATE KEY-----",
        b"-----BEGIN DSA PRIVATE KEY-----"
    }
    try:
        with open(file, 'rb') as target:
            first500Bytes = target.read(500)
    except OSError as err:
        logging.debug("Caught Exception: {}".format(err))
        return ''
    if any(header in first500Bytes for header in headers):
        first500string = first500Bytes.decode("utf-8")
        if 'ENCRYPTED' not in first500string.upper(): # excepts out keys that specify encryption details in another line
            logging.info("{}".format(file))
            if targets:
                return file
    return ''


def build_homedirs(ssh = ''):
    """ Build a dictionary of HomeDirs to be scanned, marked as todo """
    logging.debug("Reading /etc/auto.scanhomes")
    with open('/etc/auto.scanhomes') as autohomes:
        data = autohomes.readlines()
    mounts = [host.split()[0] for host in data]
    build_homes = {}
    for mount in mounts:
        nextHome = '/scanhomes/' + mount + ssh # creates full path for use from scanner
        build_homes[nextHome] = "todo"         # sets home to be scanned
    return build_homes


def build_queue(homes):
    """ Builds an iter() object queue to run scans in parallel """
    queue = []
    logging.debug("Building Queue")
    for home, uid in homes.items(): # skips homes marked as already scanned
        if uid == 'done':
            logging.debug("Already done, skipping: {}".format(home))
            continue
        queue.append(home)
    return iter(queue)

def run_scandir(homes, targets=False, yaml_config = "homes.yml"):
    """ Consumes the queue and runs the forks in parralel """
    pids = {}
    queue = build_queue(homes)

    logging.debug("Start Queue")
    for _ in range(4):            # Batches the first 4 runs
        is_next, pid, home = iterate(queue, targets)
        pids[pid] = home

    while is_next:
        try:
            catch = os.wait3(0)
            homes[pids[catch[0]]] = 'done' # updates homes when a fork is complete, by using pid lookup dict.
            logging.debug("Closing PID {}".format(catch[0]))
            is_next, pid, home = iterate(queue)
            pids[pid] = home
            dump_homes(homes, yaml_config)
        except ChildProcessError as err:
            logging.debug("Caught Exception: {}".format(err))
            continue

    for __ in range(4):
        time.sleep(5)
        try:                          # While loops ends after last iteration. This loop should
            catch = os.wait3(0)               # catch any remaining pids still open.
            homes[pids[catch[0]]] = 'done'
            logging.debug("Closing PID {}".format(catch[0]))
            dump_homes(homes, yaml_config)
        except ChildProcessError as err:
            logging.debug("Caught Exception: {}".format(err))
            continue

def dump_homes(homes, yaml_config = "homes.yml"):
    """ Save progress of scan to local yml file, done is marked by the run_scandir function"""
    with open(yaml_config, 'w') as homesyml:
        yaml.dump(homes, homesyml, default_flow_style=False)
    logging.debug("Saving to " + yaml_config)


def main(ssh = ''):
    """ main function to start and run the other functions """
    loadhomes = False            # Keep track of whether the homes.yml needs to be loaded
    if not ssh:
        try:
            if os.stat('homes.yml').st_size > 0: # Check for existing homes.yml and pass true
                loadhomes = True                 # Homes.yml will only be loaded if -ssh is not
        except OSError as err:
            logging.debug("Caught Exception: {}".format(err))                          # specified, and no homes.yml exists. A new
            pass                                 # homes.yml will always be created if -ssh is on.
    if loadhomes:
        with open('homes.yml') as homesyml:      #load homes.yml into homes as dict.
            homes = yaml.load(homesyml)
        logging.info("Yaml loaded: {} homes".format(str(len(homes))))
    else:
        homes = build_homedirs(ssh)              # Creates homes entries, and homes.yml
        dump_homes(homes)
    run_scandir(homes)


if __name__ == "__main__":
    for arg in sys.argv:         #Populates ssh if option specified. This scans only ~/.ssh/
        if "--ssh" in arg:
            ssh='/.ssh'
            break
    else:
        ssh=''

    for arg in sys.argv:         #Populates ssh if option specified. This scans only ~/.ssh/
        if "--debug" in arg:
            loglevel = logging.DEBUG
            break
    else:
        loglevel = logging.INFO

    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',filename='results.txt',level=loglevel)
    logging.info("Start Scan")
    os.chmod('results.txt', 0o666) # Creates initial log file if absent, changes permission so forks can access it

    main(ssh)
