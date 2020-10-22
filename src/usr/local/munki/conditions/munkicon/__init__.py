"""Configures logging for the utility."""
import sys; sys.dont_write_bytecode = True  # NOQA
import logging
import logging.handlers
import os


log_path = '/Library/Managed Installs/Logs/munkicon.log'
log = logging.getLogger()
log.setLevel(logging.INFO)
fh = logging.handlers.RotatingFileHandler(log_path, maxBytes=(1048576 * 10), backupCount=7)
fmt = logging.Formatter("%(asctime)s - %(name)s -  %(levelname)s - %(message)s")
fmt = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
fh.setFormatter(fmt)
log.addHandler(fh)

# if os.path.isfile(log_path):
#     fh.doRollover()

logging.getLogger(__name__)
