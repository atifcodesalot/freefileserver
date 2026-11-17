
__author__ = "Burzum"
__version__ = "1.0.0"

import logging

logging.basicConfig(level=logging.DEBUG,
                    format="[%(name)s][%(asctime)s][%(levelname)s]: %(message)s")

logger = logging.getLogger(__package__)
logger.setLevel(logging.INFO)