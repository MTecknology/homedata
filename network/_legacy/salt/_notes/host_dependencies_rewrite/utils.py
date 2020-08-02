def host_dependencies():
    '''
    Returns a merged list of containers and virtual machines running on VM hosts.
    '''
    deps = {}

    # LXC
    ret = __salt__['mine.get']('*', 'lxc.list')
    if ret:
        for host, val in ret.iteritems():
            deps[host] = [item for k, v in val.iteritems() for item in v]

    # VIRT
    ret = __salt__['mine.get']('*', 'virt.list_domains')
    if ret:
        for host, val in ret.items():
            if host in deps:
                deps[host].extend(val)
            else:
                deps[host] = val

    # HYPERV
    ret = __salt__['mine.get']('*', 'st_hyperv')
    if ret:
        for host, val in ret.iteritems():
            match = re.match('[a-z0-9\-_]+\.([a-z0-9]+)', host)
            if match:
                hostdc = match.group(1)
            else:
                continue

            names = [x['Name'].replace('.ad', '.' + hostdc) for x in val if x['Name'].endswith('.ad')]
            if names and host in deps:
                deps[host].extend(names)
            elif names:
                deps[host] = names

    return deps
