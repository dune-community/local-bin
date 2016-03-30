#!/usr/bin/env python
import sys

from localscripts import build_external_libraries


if __name__ == '__main__':
    sys.exit(build_external_libraries.build_all())
