#!/usr/bin/env python
import sys

from localscripts import build_dune_modules


if __name__ == '__main__':
    sys.exit(build_dune_modules.build_modules())