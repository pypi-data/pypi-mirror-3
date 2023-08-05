"""
This uses Paramiko to send files from workers to other workers (without having
to go through the master).
"""

from reductio import para_ssh
from reductio import config
import logging
import os
LOG = logging.getLogger(__name__)

def send_file(connection, source_path, target_path):
    """
    `source_path` is the absolute path of the file to send.
    `target_path` is the relative path of where to put it.
    """
    absolute_target = os.path.join(connection.reductio_home, target)
    target_dir = os.path.dirname(absolute_target)
    connection.execute("mkdir -p %s" % target_dir)
    connection.put(source_path, absolute_target)

def make_connections():
    """
    Get an ssh.Connection object for each worker that we can successfully
    contact and run reductio on.
    """
    connections = []
    for worker_config in config.WORKERS:
        conn = ssh.Connection(**worker_config)
        if worker_config['virtualenv']:
            conn.execute("source %s/bin/activate" % worker_config['virtualenv'])
        try:
            output = conn.execute("python -m reductio.config HOMEDIR")[0].strip()
        except:
            log.warn("Could not connect to %r" % worker_config)
            continue
        conn.reductio_home = output[0].strip()
        connections.append(conn)
    if len(connections) == 0:
        raise IOError("reductio could not connect to any workers.")
    return connections

CONNECTIONS = None

def get_connections():
    """
    Get the list of connections if it already exists; create it using
    `make_connections` if not.
    """
    global CONNECTIONS
    if CONNECTIONS is None:
        CONNECTIONS = make_connections()
    return CONNECTIONS

def close_connections():
    if CONNECTIONS is not None:
        for conn in CONNECTIONS:
            conn.close()
    CONNECTIONS = None

def __del__():
    close_connections()

