import os
import subprocess
import sys

try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker

# Keys: 'filevault_active'
#       'filevault_deferral'
#       'filevault_institution_key'
#       'filevault_personal_key'
#       'filevault_status'
#       'filevault_users'
#       'filevault_encryption_in_progress'
#       'filevault_decryption_in_progress'
#       'filevault_users'


class FileVaultConditions(object):
    """FileVault conditions."""
    def __init__(self):
        self.conditions = self._process()

    def _fdesetup(self, verb):
        """Executes the `fdesetup` command and processes output."""
        result = None

        if os.geteuid() == 0:
            _cmd = ['/usr/bin/fdesetup', verb]

            _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _r, _e = _p.communicate()

            if _p.returncode == 0 or (verb == 'showdeferralinfo' and _p.returncode == 20):
                if _r:
                    if isinstance(_r, bytes):
                        _r = _r.decode('utf-8').strip()

                    result = _r
        else:
            sys.exit(1)

        return result

    def _status(self):
        """FileVault Status."""
        result = {'filevault_status': '',
                  'filevault_encryption_in_progress': '',
                  'filevault_decryption_in_progress': ''}

        _result = self._fdesetup(verb='status')

        if _result:
            for _l in _result.splitlines():
                _l = _l.strip()

                if 'FileVault is ' in _l:
                    result['filevault_status'] = _l.replace('FileVault is ', '').lower().replace('.', '')

                result['filevault_encryption_in_progress'] = 'Encryption in progress: Percent completed = ' in _l
                result['filevault_decryption_in_progress'] = 'Decryption in progress: Percent completed = ' in _l

        return result

    def _is_active(self):
        """FileVault on and active. Differs to 'status'."""
        result = {'filevault_active': ''}

        try:
            result['filevault_active'] = 'true' in self._fdesetup(verb='isactive')
        except TypeError:
            pass

        return result

    def _users(self):
        """FileVault Users."""
        result = {'filevault_users': ''}

        _result = self._fdesetup(verb='list')

        # The UUID in the command output is stripped as this is not necessarily known.
        if _result:
            result['filevault_users'] = [_l.strip().split(',')[0] for _l in _result.splitlines()]

        return result

    def _deferral_info(self):
        """Deferrals"""
        result = {'filevault_deferral': ''}

        _result = self._fdesetup(verb='showdeferralinfo')

        if _result:
            for _l in _result.splitlines():
                _l = _l.strip()

                result['filevault_deferral'] = 'active' if 'Defer' in _l else 'not_found'
                break

        return result

    def _has_personal_key(self):
        """Personal recovery key."""
        result = {'filevault_personal_key': ''}

        result['filevault_personal_key'] = 'true' in self._fdesetup(verb='haspersonalrecoverykey')

        return result

    def _has_institution_key(self):
        """Personal recovery key."""
        result = {'filevault_institution_key': ''}

        result['filevault_institution_key'] = 'true' in self._fdesetup(verb='hasinstitutionalrecoverykey')

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._status())
        result.update(self._is_active())
        result.update(self._users())
        result.update(self._deferral_info())
        result.update(self._has_personal_key())
        result.update(self._has_institution_key())

        return result


def runner(dest):
    fde = FileVaultConditions()
    mc = worker.MunkiConWorker(conditions_file=dest, log_src=__file__)

    mc.write(conditions=fde.conditions)
