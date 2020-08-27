#!/usr/bin/env python3

from localscripts.gen_path import gen_path
from localscripts.common import make_config

if __name__ == '__main__':
    gen_path(local_config=make_config())
