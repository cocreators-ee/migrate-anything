from __future__ import absolute_import

import logging

LOG_FORMAT = "%(asctime)s (%(process)d) [%(levelname)8s]: %(message)s"

logging.basicConfig(format=LOG_FORMAT, level="INFO")
logger = logging.getLogger(__name__)
