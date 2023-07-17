#!/usr/bin/env python

import sys
import re
from git import Repo
from decouple import Config, RepositoryEnv

config = Config(RepositoryEnv(".env.local"))

if __name__ == "__main__":
    for arg in sys.argv:
        print(arg)
    sys.exit(1)


def put_as_githook():
    import shutil

    shutil.copy(__file__, ".git/hooks/")
    shutil.move(".git/hooks/pre_commit_msg.py", ".git/hooks/prepare-commit-msg")
