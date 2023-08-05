from fabric.api import env, task, run, sudo, put, serial
import config
import os

env.parallel = True
env.hosts = config.FABRIC_HOSTS

def map(function, source, target):
    run('python -m reductio.operate map %s %s %s' % (function, source, target))

def reduce(function, source, target):
    run('python -m reductio.operate reduce %s %s %s' % (function, source, target))

def transform(function, source, target):
    run('python -m reductio.operate transform %s %s %s' % (function, source, target))

def initialize(function, target):
    run('python -m reductio.operate initialize %s %s %s' % (target, target))

def scatter(source, target):
    run('python -m reductio.operate scatter %s %s' % (source, target))

def sort(source, target):
    run('python -m reductio.operate sort %s %s' % (source, target))

def sort_unique(source, target):
    run('python -m reductio.operate sort_unique %s %s' % (source, target))

def delete(source):
    run('python -m reductio.operate delete %s %s' % (source, source))

# TODO: account for virtualenvs defined in config
@serial
def install_package(package_name):
    env = run('echo $VIRTUAL_ENV')
    if env.strip():
        run('easy_install -U %s' % package_name)
    else:
        sudo('easy_install -U %s' % package_name)

@serial
@task
def install_reductio():
    install_package('reductio')

@serial
@task
def configure_ubuntu():
    uname = run('uname -a')
    if 'Ubuntu' in uname:
        sudo('aptitude update')
        sudo('aptitude install -y python-setuptools python-dev build-essential')

@task
def get_worker_home():
    return run('python -m reductio.config HOMEDIR').strip()

def put_in_directory(source_path, target_path):
    target_path = str(run('echo %s' % target_path))
    run('mkdir -p '+os.path.dirname(target_path))
    if env.host != config.HOSTNAME or source_path != target_path:
        put(source_path, target_path)
    else:
        print "Skipping identical file"

# TODO: we might not keep the config in HOMEDIR
@task
def deploy_worker_config(dir=None):
    if dir is None:
        dir = '~/.reductio'
    source_file = os.path.join(config.HOMEDIR, 'workers.cfg')
    target_file = os.path.join(dir, 'workers.cfg')
    put_in_directory(source_file, target_file)

