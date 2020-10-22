#!/usr/local/munki/python
import os
import subprocess

try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker

# Keys: 'mac_os_python_path'
#       'mac_os_python_ver'
#       'munki_python_path'
#       'munki_python_symlink'
#       'munki_python_ver'
#       'official_python3_path'
#       'official_python3_ver'


class PythonConditions(object):
    """Generates information about python versions."""
    def __init__(self):
        self.conditions = self._process()

    def _python_versions(self):
        """Gets the version of several Python paths (if they exist)."""
        result = {'mac_os_python_path': '',
                  'mac_os_python_ver': '',
                  'munki_python_path': '',
                  'munki_python_symlink': '',
                  'munki_python_ver': '',
                  'official_python3_path': '',
                  'official_python3_ver': ''}

        _munki_pythons = ['/usr/local/munki/python', '/usr/local/munki/munki-python']
        _munki_python = [_x for _x in _munki_pythons if os.path.exists(_x)][0]

        _python_paths = {'mac_os_python_path': '/usr/bin/python',
                         'munki_python_path': _munki_python,
                         'official_python3_path': '/usr/local/bin/python3'}

        for _k, _v in _python_paths.items():
            if os.path.exists(_v):
                _real_path = os.path.realpath(_v)
                result[_k] = _real_path

                # Include the munki python symlink in use
                if _k == 'munki_python_path':
                    result['munki_python_symlink'] = _v

                _cmd = [_real_path, '--version']

                _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                _r, _e = _p.communicate()

                if _p.returncode == 0:
                    _ver = None

                    if _r:
                        if isinstance(_r, bytes):
                            _r = _r.decode('utf-8').strip()

                        _ver = _r.replace('Python ', '')
                    elif _e:
                        if isinstance(_e, bytes):
                            _e = _e.decode('utf-8').strip()

                        _ver = _e.replace('Python ', '')

                    result[_k.replace('_path', '_ver')] = _ver
        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._python_versions())

        return result


def main():
    py = PythonConditions()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=py.conditions)


if __name__ == '__main__':
    main()
