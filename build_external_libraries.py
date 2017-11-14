#!/usr/bin/env python
import sys

from localscripts import build_external_libraries
from localscripts.common import make_config


if __name__ == '__main__':
    sys.exit(build_external_libraries.build_all(local_config=make_config()))
