import subprocess

def sort(filename_in, filename_out, unique=False):
    if unique:
        subprocess.check_call(['sort', filename_in, '-u', '-o', filename_out])
    else:
        subprocess.check_call(['sort', filename_in, '-o', filename_out])
