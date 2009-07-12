import logging
from commands import logger


def clone():
    logger.error("""The `gs-clone` command has been removed. It is performed
as part of the gitify process.
    """)


def fetch():
    logger.error("""The `gs-fetch` command is deprecated. Use `gitify fetch`
instead.
    """)


def commit():
    logger.error("""The `gs-commit` command is deprecated. Use `gitify push`
instead.
    """)

logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(ch)
