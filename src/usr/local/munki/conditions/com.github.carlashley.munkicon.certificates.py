#!/usr/local/munki/python
import subprocess

try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker

# Keys: 'certificates_sha256'
#       'certificates_sha1'


class Certificate():
    """Certificates."""
    def __init__(self):
        self.conditions = self._process()

    def _find_certificates(self):
        """SHA256 and SHA1 values."""
        result = {'certificates_sha256': list(),
                  'certificates_sha1': list()}
        _sha1 = set()
        _sha256 = set()
        _sha1_prefix = 'SHA-1 hash: '
        _sha256_prefix = 'SHA-256 hash: '

        _cmd = ['/usr/bin/security', 'find-certificate', '-a', '-Z', '/Library/Keychains/System.keychain']
        _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _r, _e = _p.communicate()

        if _p.returncode == 0:
            if _r:
                if isinstance(_r, bytes):
                    _r = _r.decode('utf-8').strip()

                for _l in _r.splitlines():
                    _l = _l.strip()

                    if _l.startswith(_sha256_prefix):
                        _hash = _l.replace(_sha256_prefix, '')
                        _sha256.add(_hash)
                    elif _l.startswith(_sha1_prefix):
                        _hash = _l.replace(_sha1_prefix, '')
                        _sha1.add(_hash)

        result['certificates_sha1'] = list(_sha1)
        result['certificates_sha256'] = list(_sha256)

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._find_certificates())

        return result


def main():
    certs = Certificate()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=certs.conditions)


if __name__ == '__main__':
    main()
