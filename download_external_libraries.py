#!/usr/bin/env python3

import sys
import localscripts.download_external_libraries as dl
from localscripts.common import make_config


if __name__ == '__main__':
    sys.exit(dl.download_all(local_config=make_config()))
