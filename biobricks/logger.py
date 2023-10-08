import logging
import sys

logger = logging.getLogger(__name__)

# Create a handler that outputs to stderr
handler = logging.StreamHandler(sys.stderr)

# Define a more visually appealing formatter
formatter = logging.Formatter(
    '\033[1;36m%(asctime)s\033[0m | \033[1;33m%(levelname)s\033[0m: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.INFO)
