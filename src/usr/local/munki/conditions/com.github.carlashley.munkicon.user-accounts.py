#!/usr/local/munki/python
import subprocess

try:
    from munkicon import plist
    from munkicon import worker
except ImportError:
    from .munkicon import plist
    from .munkicon import worker

# Keys: 'user_home_path'


class UserAccounts(object):
    def __init__(self):
        self.conditions = self._process()

    def _users(self):
        """Users."""
        result = set()

        _ignore_users = ['daemon',
                         'nobody',
                         'root']

        _cmd = ['/usr/bin/dscl', '.', '-list', '/Users']

        _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _r, _e = _p.communicate()

        if _p.returncode == 0:
            if isinstance(_r, bytes):
                _r = _r.decode('utf-8').strip()

            for _u in _r.splitlines():
                if not _u.startswith('_'):
                    if _u not in _ignore_users:
                        result.add(_u)

        return result

    def _home_dirs(self):
        """Home Directories"""
        result = {'user_home_path': list()}

        _users = self._users()

        _home_dirs = set()

        if _users:
            for _u in _users:
                _cmd = ['/usr/bin/dscl', '-plist', '.', '-read', '/Users/{}'.format(_u), 'NFSHomeDirectory']

                _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _r, _e = _p.communicate()

                if _p.returncode == 0:
                    if isinstance(_r, bytes):
                        _r = _r.decode('utf-8').strip()

                    if _r:
                        _h = plist.readPlistFromString(_r)['dsAttrTypeStandard:NFSHomeDirectory']

                        if _h:
                            try:
                                _r = '{},{}'.format(_u, _h[0].strip())
                            except IndexError:
                                _r = '{},{}'.format(_u, _h.strip())

                            _home_dirs.add(_r)

        result['user_home_path'] = list(_home_dirs)

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._home_dirs())

        return result


def main():
    users = UserAccounts()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=users.conditions)


if __name__ == '__main__':
    main()
