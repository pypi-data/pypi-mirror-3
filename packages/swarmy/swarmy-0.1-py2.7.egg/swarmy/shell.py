import os
import subprocess
import sys

def pipe_to_pager(text, command=None):
    """ Pipe text to a pager and wait for the user to exit the pager. """
    if command is None:
        command = os.environ['PAGER'] if 'PAGER' in os.environ else 'more'
    pager = subprocess.Popen(command, stdin=subprocess.PIPE)
    print >> pager.stdin, text,
    pager.stdin   = sys.stdin
    pager.wait()
