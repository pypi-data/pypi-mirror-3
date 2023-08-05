from fabric.api import env, task, run, local, sudo, cd, put, serial, roles, settings, hide
from reductio import operate
import pkgutil
import config
import os

env.parallel = True
env.roledefs = {
    'workers': config.FABRIC_HOSTS
}
env.key_filename = os.path.expanduser(config.KEY_FILENAME)

# redefine exists, based on the version in fabric.contrib.files, so that it
# will expand the home directory
def exists(path):
    cmd = 'test -e %s' % path
    with settings(hide('everything'), warn_only=True):
        return not run(cmd).failed

def exists_local(path):
    return os.access(path, os.F_OK)

@task
@roles('workers')
def map(function, source, target):
    run('python -m reductio.operate map %s %s %s' % (function, source, target))

@task
@roles('workers')
def reduce(function, source, target):
    run('python -m reductio.operate reduce %s %s %s' % (function, source, target))

@task
@roles('workers')
def transform(function, source, target):
    run('python -m reductio.operate transform %s %s %s' % (function, source, target))

@task
def initialize(function, source, target):
    # not a Fabric task -- only run it once, on the local machine
    operate.run('initialize', function, source, source)
    operate.run('scatter', source, target)

@task
def initial_scatter(source, target):
    operate.run('scatter', source, target)

@task
@serial
@roles('workers')
def scatter(source, target):
    run('python -m reductio.operate scatter %s %s' % (source, target))

@task
@roles('workers')
def sort(source, target):
    run('python -m reductio.operate sort %s %s' % (source, target))

@task
@roles('workers')
def sort_unique(source, target):
    run('python -m reductio.operate sort_unique %s %s' % (source, target))

@task
@roles('workers')
def delete(source):
    local('python -m reductio.operate delete %s %s' % (source, source))
    run('python -m reductio.operate delete %s %s' % (source, source))

@task
@roles('workers')
def merge(source, target):
    remote_home = run('python -m reductio.config HOMEDIR')
    remote_dir = os.path.join(remote_home, source)
    host = env.host
    local_parent = os.path.join(config.HOMEDIR, target)
    local_dir = os.path.join(config.HOMEDIR, target, env.host)
    key_file = config.KEY_FILENAME
    local('mkdir -p %s' % local_dir)
    local('scp -o StrictHostKeyChecking=no -i %s %s:%s/* %s/' % (key_file, host, remote_dir, local_dir))
    local('sort -m %s/*/*.txt > %s/merged.txt' % (local_parent, local_parent))

# TODO: account for virtualenvs defined in config
@task
@roles('workers')
def install_package(package_name):
    run('source ~/.bashrc')
    virtualenv = run('echo $VIRTUAL_ENV')
    if virtualenv.strip():
        run('easy_install -U %s' % package_name)
    else:
        sudo('easy_install -U %s' % package_name)

@task
@serial
@roles('workers')
def install_git_package(git_owner, package_name, branch='master'):
    code_dir = config.CODE_DIR
    run('source ~/.bashrc')
    run('mkdir -p %s' % code_dir)
    repo_dir = '%s/%s' % (code_dir, package_name)
    if not exists(repo_dir):
        with cd(code_dir):
            run('git clone git://github.com/%s/%s.git' % (git_owner, package_name))
    with cd(repo_dir):
        run('git pull origin %s' % branch)
        run('git checkout %s' % branch)
        env = run('echo $VIRTUAL_ENV')
        if env.strip():
            run('python setup.py develop')
        else:
            sudo('python setup.py develop')

#@task
#@roles('workers')
#def update_dev_project(package):
#    code_dir = config.CODE_DIR
#    run('source ~/.bashrc')
#    run('mkdir -p %s' % code_dir)
#    repo_dir = '%s/%s' % (code_dir, package)
#    
#    initfile = pkgutil.find_loader(package).get_filename()
#    dir = os.path.dirname(os.path.dirname(initfile))
#    if not exists_local(os.path.join(dir, 'setup.py')):
#        raise IOError("Can't find %s/setup.py. This probably means the project"
#                      " was not installed using 'setup.py develop'."
#                      % dir)
#    command = "rsync -avuz --delete %s/ %s:%s" % (dir, env.host, code_dir)
#    local(command)
#
#    with cd(repo_dir):
#        virtualenv = run('echo $VIRTUAL_ENV')
#        if virtualenv.strip():
#            run('python setup.py develop')
#        else:
#            sudo('python setup.py develop')

@task
@serial
@roles('workers')
def install_reductio():
    install_git_package('rspeer', 'reductio', 'master')
    put_in_directory('~/.reductio/reductio.cfg', '~/.reductio/reductio.cfg')

@task
@serial
@roles('workers')
def configure_ubuntu():
    uname = run('uname -a')
    if 'Ubuntu' in uname:
        sudo('aptitude update')
        sudo('aptitude install -y -q python-setuptools python-dev build-essential git')

def get_worker_home():
    return run('python -m reductio.config HOMEDIR').strip()

def put_in_directory(source_path, target_path):
    target_path = str(run('echo %s' % target_path))
    source_path = os.path.expanduser(source_path)
    run('mkdir -p '+os.path.dirname(target_path))
    if env.host != config.HOSTNAME or source_path != target_path:
        put(source_path, target_path)
        print "%s => %s" % (source_path, target_path)
    else:
        print "Skipping identical file"

# TODO: we might not keep the config in HOMEDIR
@task
@roles('workers')
def deploy_worker_config(dir=None):
    if dir is None:
        dir = '~/.reductio'
    source_file = os.path.join(config.HOMEDIR, 'workers.cfg')
    target_file = os.path.join(dir, 'workers.cfg')
    put_in_directory(source_file, target_file)

