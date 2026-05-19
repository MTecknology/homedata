def parse_ansible_log(logfile):
    with open(logfile) as deploy:
        data = deploy.readlines()

    for num, line in enumerate(data):
        if "RECAP" in line:
            logonly = data[:num]
            results = data[(num + 1):]

    hosts = {}
    for line in results:
        hostname = line.split()[5]
        hosts[hostname] = []
        hosts[hostname].append(line.strip())

    for host in hosts.keys():
        for line in logonly:
            if host in line:
                hosts[host].append(line.strip())

    return hosts

if __name__ == "__main__":

    hosts = parse_ansible_log("deploy.log")

    unreachable = []
    failed = []
    success = []

    for host in hosts.keys():
        if "unreachable=1" in hosts[host][0]:
            unreachable.append(host)
        if "failed=1" in hosts[host][0]:
            if "and repo_installed" in hosts[host][-1]:
                success.append(host)
            elif "/bin/python" in hosts[host][-1]:
                continue
            else:
                failed.append(host)
        if "failed=0" in hosts[host][0] and "unreachable=0" in hosts[host][0]:
            success.append(host)
        # if "/bin/python" in hosts[host][-1]:
        #     print(host + " ansible_python_interpreter=/usr/local/bin/python")
    hostsuccess = {}
    hostfails = {}

    # print("__________________SUCCESS________________________")
    # [print(line) for line in success]

    for host in success:
        hostsuccess[host] = "successful"

    # print("__________________UNREACHABLE____________________")
    # [print(line) for line in unreachable]
    for host in unreachable:
        if "uthent" in hosts[host][-1]:
            hostfails[host] = "authentication error"
        elif "Name or service not known" in hosts[host][-1]:
            hostfails[host] = "DNS Error"
        elif "timed out" in hosts[host][-1]:
            hostfails[host] = "timed out"
        elif "SSH protocol" in hosts[host][-1]:
            hostfails[host] = "ssh protocol"
        elif "Unable to connect to port 22" in hosts[host][-1]:
            hostfails[host] = "Unable to connect to port 22"
        elif "Network is unreachable" in hosts[host][-1]:
            hostfails[host] = "Network is unreachable"
        else:
            hostfails[host] = hosts[host][-1]

    # print("__________________FAILED_________________________")
    #[print(line) for line in failed]

    for host in failed:
        if "cache_update" in hosts[host][-1]:
            hostfails[host] = "apt error"
        elif "simplejson" in hosts[host][-1].lower():
            hostfails[host] = "simplejson error"
        elif "arch.rc" in hosts[host][-1].lower():
            hostfails[host] = "simplejson error"
        elif "is listed more than once" in hosts[host][-1].lower():
            hostfails[host] = "Repo is listed more than once"
        elif "python2 bindings for rpm" in hosts[host][-1].lower():
            hostfails[host] = "python2 bindings for rpm"
        elif "found available" in hosts[host][-1].lower():
            hostfails[host] = "No package matching"
        elif "repomd.xml" in hosts[host][-1].lower():
            hostfails[host] = "HTTP Error 404"
        elif "baseurl" in hosts[host][-1].lower():
            hostfails[host] = "Cannot find a valid baseurl"
        elif "yum_base" in hosts[host][-1].lower():
            hostfails[host] = "YumBase' object has no attribute 'preconf'"
        else:
            hostfails[host] = hosts[host][-1]

    for key,value in hostsuccess.items():
        print(key,'#',value)

    for key,value in hostfails.items():
        print(key,'#',value)
