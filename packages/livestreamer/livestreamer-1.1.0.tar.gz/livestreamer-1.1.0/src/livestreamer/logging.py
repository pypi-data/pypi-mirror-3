#!/usr/bin/env python

import logging
from logging import WARNING, INFO, DEBUG

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"

logging.basicConfig(format=LOG_FORMAT, datefmt="%H:%M:%S")

logger = logging.getLogger(name)
logger.setLevel(logging.INFO)
