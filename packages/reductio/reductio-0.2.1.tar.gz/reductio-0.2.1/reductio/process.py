import subprocess
import config
import os

def sort(filenames_in, filename_out, unique=False):
    home = config.HOMEDIR
    tempdir = '%s/tmp' % home
    os.system('mkdir -p %s' % tempdir)
    filenames_in = list(filenames_in)
    if unique:
        subprocess.check_call(['sort'] + filenames_in + ['-u', '-o', filename_out, '-T', tempdir])
    else:
        subprocess.check_call(['sort'] + filenames_in + ['-o', filename_out, '-T', tempdir])
