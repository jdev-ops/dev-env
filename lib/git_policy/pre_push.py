#!/usr/bin/env python

import sys
import subprocess

for line in sys.stdin:
    local_ref, local_sha1, remote_ref, remote_sha1 = line.strip().split()
    message = subprocess.check_output(
        ['git', 'log', '--format=format:%H', local_sha1, f"^{remote_sha1}"])
    for sha in message.decode("UTF-8").split("\n"):
        try:
            res = subprocess.check_output(
                ['git', 'verify-commit', '-v', sha])
        except subprocess.CalledProcessError as e:
            print(e)
            sys.exit(1)

def put_as_pre_push_githook():
    import shutil

    shutil.copy(__file__, ".git/hooks/")
    shutil.move(".git/hooks/pre_push.py", ".git/hooks/pre-push")
