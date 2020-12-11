#!/usr/local/munki/python
import re
import subprocess

from datetime import datetime

try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker

# Keys: 'certificates_sha1'
#       'certificates_sha1_dates'
#       'certificates_sha256'
#       'certificates_sha246_dates'


class Certificate():
    """Certificates."""
    def __init__(self):
        self.conditions = self._process()

    def _parse_date(self, prefix, val):
        result = None
        _timezone = val.strip().split()[-1]
        _in_fmt = '%b %d %H:%M:%S %Y {}'.format(_timezone)
        _out_fmt = '%Y-%m-%d %H:%M:%S {}'.format(_timezone)

        _r = val.replace('{}='.format(prefix), '').strip()
        _r = datetime.strptime(_r, _in_fmt)
        _r = datetime.strftime(_r, _out_fmt)

        result = _r

        return result

    def _openssl_expiration(self, cert):
        """Get notBefore and notAfter dates of certificate using OpenSSL"""
        result = None
        _bfr_date = None
        _end_date = None

        # Note, use 'stdin' to 'pipe' certificate through
        _cmd = ['/usr/bin/openssl', 'x509', '-dates', '-noout']
        _p = subprocess.Popen(_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _p.stdin.write(cert)
        _r, _e = _p.communicate()

        if _p.returncode == 0 and _r:
            if isinstance(_r, bytes):
                _r = _r.decode('utf-8').strip()

            for _l in _r.splitlines():
                _l = re.sub('\s+', ' ', _l)

                # Convert the time details to a YYYY-MM-DD H:M:S TZ
                # format
                if 'notBefore' in _l:
                    _bfr_date = self._parse_date(prefix='notBefore', val=_l)

                if 'notAfter' in _l:
                    _end_date = self._parse_date(prefix='notAfter', val=_l)

            if _bfr_date and _end_date:
                result = '{} to {}'.format(_bfr_date, _end_date)

        return result
        # openssl x509 -enddate -noout

    def _find_certificates(self):
        """Find certificates and process dates.."""
        result = {'certificates_sha1': list(),
                  'certificates_sha1_dates': list(),
                  'certificates_sha256': list(),
                  'certificates_sha256_dates': list()}
        _end_cert_str = '-----END CERTIFICATE-----'
        _sha1_prefix = 'SHA-1 hash: '
        _sha256_prefix = 'SHA-256 hash: '

        _cmd = ['/usr/bin/security', 'find-certificate', '-a', '-p', '-Z', '/Library/Keychains/System.keychain']

        _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _r, _e = _p.communicate()

        if _p.returncode == 0 and _r:
            if isinstance(_r, bytes):
                _r = _r.decode('utf-8').strip()

                for _cert in _r.split(_end_cert_str):
                    _sha1 = None
                    _sha256 = None

                    for _l in _cert.splitlines():
                        if _sha1_prefix in _l:
                            _sha1 = _l
                        elif _sha256_prefix in _l:
                            _sha256 = _l

                    if _sha1:
                        _sha1 = _sha1.replace(_sha1_prefix, '')

                        if _sha1 not in result['certificates_sha1']:
                            result['certificates_sha1'].append(_sha1)

                    if _sha256:
                        _sha256 = _sha256.replace(_sha256_prefix, '')

                        if _sha256 not in result['certificates_sha256']:
                            result['certificates_sha256'].append(_sha256)

                    if 'BEGIN CERTIFICATE' in _cert:
                        _cert = str('{}{}'.format(_cert, _end_cert_str).strip()).encode()
                        _dates = self._openssl_expiration(cert=_cert)

                        if (_sha1, _sha256, _dates):
                            _sha1_result = '{},{}'.format(_sha1, _dates)
                            _sha256_result = '{},{}'.format(_sha256, _dates)

                            if _sha1_result not in result['certificates_sha1_dates']:
                                result['certificates_sha1_dates'].append(_sha1_result)

                            if _sha256_result not in result['certificates_sha256_dates']:
                                result['certificates_sha256_dates'].append(_sha256_result)

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
