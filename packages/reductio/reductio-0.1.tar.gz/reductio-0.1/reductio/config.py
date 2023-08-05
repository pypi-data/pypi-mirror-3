import os
import sys
import socket
import json
import ConfigParser

HOSTNAME = socket.gethostname()
HOMEDIR = os.path.expanduser('~/.reductio')
PARTITIONS = 64

def get_worker_config(dirlist):
    worker_config = ConfigParser.ConfigParser()
    file_possibilities = [os.path.join(dir, 'workers.cfg') for dir in dirlist]
    got = worker_config.read(file_possibilities)
    workers = []
    for section in worker_config.sections():
        worker_dict = {}
        for key, value in worker_config.items(section):
            worker_dict[key] = value
        workers.append(worker_dict)
    return workers

def worker_to_fabric(worker):
    if 'username' in worker:
        hoststr = worker['username'] + '@' + worker['host']
    else:
        hoststr = worker['host']
    if 'password' in worker:
        from fabric import env
        env.passwords[hoststr] = worker['password']
    return hoststr

WORKERS = get_worker_config(['.', HOMEDIR])
FABRIC_HOSTS = [worker_to_fabric(w) for w in WORKERS]
#global_config = ConfigParser.ConfigParser()
#global_config.read([os.path.join(HOMEDIR, 'reductio.cfg')])

def main(command, *args):
    if command in globals():
        print globals()[command]
    else:
        raise ValueError("There is no configuration option called %s.\n" % command)

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.stderr.write("Usage: python -m reductio.config (command)\n")
    main(*sys.argv[1:])
