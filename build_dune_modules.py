#!/usr/bin/env python
import sys

from localscripts import build_dune_modules
from localscripts.common import make_config


if __name__ == '__main__':
    sys.exit(build_dune_modules.build_modules(local_config=make_config()))
