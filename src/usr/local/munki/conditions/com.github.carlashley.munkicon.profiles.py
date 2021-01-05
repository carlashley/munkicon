#!/usr/local/munki/munki-python
import subprocess

try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker

# Keys: 'installed_profiles'


class Profiles():
    """Certificates."""
    def __init__(self):
        self.conditions = self._process()

    def _find_certificates(self):
        """Find certificates and process dates.."""
        result = {'installed_profiles': list()}
        _attr_str = 'attribute: name:'

        _cmd = ['/usr/bin/profiles', 'list', '-verbose']

        _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _r, _e = _p.communicate()

        if _p.returncode == 0 and _r:
            if isinstance(_r, bytes):
                _r = _r.decode('utf-8').strip()

            for _l in _r.splitlines():
                _l = _l.strip()

                if _attr_str in _l:
                    # Partition and get the last result which should be the action profile name.
                    try:
                        _result = _l.partition(_attr_str)[-1].strip()

                        if _result not in result['installed_profiles']:
                            result['installed_profiles'].append(_result)
                    except IndexError:
                        pass

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._find_certificates())

        return result


def main():
    profiles = Profiles()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=profiles.conditions)


if __name__ == '__main__':
    main()
