import os
import sys
import socket
import json
import ConfigParser

HOSTNAME = socket.gethostname()
HOMEDIR = os.path.expanduser('~/.reductio')

def get_config(dirlist, filename):
    config = ConfigParser.ConfigParser()
    file_possibilities = [os.path.join(dir, filename) for dir in dirlist]
    config.read(file_possibilities)
    return config

def get_worker_config(dirlist):
    worker_config = get_config(dirlist, 'workers.cfg')
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
        from fabric.api import env
        env.passwords[hoststr] = worker['password']
    return hoststr

_global_config = get_config(['.', HOMEDIR], 'reductio.cfg')
WORKERS = get_worker_config(['.', HOMEDIR])
KEY_FILENAME = _global_config.get('reductio', 'key_filename')
PARTITIONS = len(WORKERS)
CODE_DIR = _global_config.get('reductio', 'code_dir')

FABRIC_HOSTS = [worker_to_fabric(w) for w in WORKERS]

def main(command, *args):
    if command in globals():
        print globals()[command]
    else:
        raise ValueError("There is no configuration option called %s.\n" % command)

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        sys.stderr.write("Usage: python -m reductio.config (command)\n")
    main(*sys.argv[1:])
