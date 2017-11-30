#!/usr/bin/env python3

import sys
from pathlib import Path
from configparser import SafeConfigParser as sf


try:
    env_base_dir = Path(sys.argv[1])
except IndexError:
    env_base_dir = Path(__file__).parent.parent.joinpath('environments').resolve()

for env_dir in env_base_dir.iterdir():
    if not env_dir.is_dir():
        continue
    ext_cfg = env_dir / 'external-libraries.cfg'
    f = sf()
    f.readfp(open(ext_cfg, 'rt'))
