"""munkicon worker module"""
import logging
import os
import sys

try:
    import plist
except ImportError:
    from . import plist

LOG = logging.getLogger(__name__)


class MunkiConWorker(object):
    """MunkiConWorker"""
    def __init__(self, conditions_file='/Library/Managed Installs/ConditionalItems.plist', log_src=None):
        self._log_src = os.path.basename(log_src) if log_src else None
        self._conditions_file = conditions_file

        if not self._is_root():
            LOG.info('%s: Must be root to execute.' % self._log_src)
            sys.exit(1)

    def _is_root(self):
        result = None

        result = os.geteuid() == 0

        return result

    def _read_conditions(self):
        """Read any existing conditions in the conditional items property list file."""
        result = dict()

        if os.path.exists(self._conditions_file):
            result = plist.readPlist(path=self._conditions_file)

        return result

    def write(self, conditions):
        _data = self._read_conditions()

        if not _data:
            _data = dict()

        _data.update(conditions)

        try:
            plist.writePlist(path=self._conditions_file, data=_data)

            if _data:
                LOG.info('%s: Conditions written.' % self._log_src)
            elif not _data:
                LOG.info('%s: No conditions written.' % self._log_src)

            sys.exit(0)
        except Exception as e:
            LOG.error('%s' % e)
