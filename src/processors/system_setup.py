import os
import subprocess

from pathlib import Path

try:
    from munkicon import common
    from munkicon import worker
    from munkicon import plist
except ImportError:
    from .munkicon import common
    from .munkicon import worker
    from .munkicon import plist

# Keys: 'ard_enabled'
#       'cups_web_interface_enabled'
#       'efi_password_enabled'
#       'efi_password_supported'
#       'ntp_enabled'
#       'ntp_servers'
#       'printer_sharing_enabled'
#       'remote_apple_events_enabled'
#       'sip_enabled'
#       'ssh_enabled'
#       'timezone'
#       'wake_on_lan'
#       'rosetta2_installed'
#       'rosetta2_version'


class SystemSetupConditions(object):
    """SystemSetup conditions."""
    def __init__(self):
        self.conditions = self._process()

    def _arch(self):
        """Internal arch check as some features not supported on Apple Silicon."""
        result = None

        _cmd = ['/usr/bin/arch']

        _p = subprocess.run(_cmd, capture_output=True, encoding='utf-8')

        if _p.returncode == 0:
            result = _p.stdout.strip()

        return result

    def _ard_state(self):
        """ARD State."""
        result = {'ard_enabled': ''}

        _cmd = ['/usr/libexec/mdmclient', 'QuerySecurityInfo']

        _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _r, _e = _p.communicate()

        if _p.returncode == 0:
            if _r:
                if isinstance(_r, bytes):
                    _r = _r.decode('utf-8').strip()

                for _l in _r.splitlines():
                    _l = _l.strip()

                    if 'RemoteDesktopEnabled' in _l:
                        result['ard_enabled'] = '1' in _l
                        break

        return result

    def _efi_password_state(self):
        """EFI Password State."""
        result = {'efi_password_enabled': '',
                  'efi_password_supported': ''}
        _arch = self._arch()

        if 'arm' not in _arch:
            _cmd = ['/usr/sbin/firmwarepasswd', '-check']

            _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _r, _e = _p.communicate()

            if _p.returncode == 0:
                if _r:
                    if isinstance(_r, bytes):
                        _r = _r.decode('utf-8').strip()

                    result['efi_password_enabled'] = 'Yes' in _r.split(': ')
                    result['efi_password_supported'] = True
        elif 'arm' in _arch:
            result['efi_password_enabled'] = False
            result['efi_password_supported'] = False

        return result

    def _printer_state(self):
        """Printer State."""
        result = {'cups_web_interface_enabled': '',
                  'printer_sharing_enabled': ''}

        _cmd = ['/usr/sbin/cupsctl']

        _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _r, _e = _p.communicate()

        if _p.returncode == 0:
            if _r:
                if isinstance(_r, bytes):
                    _r = _r.decode('utf-8').strip()

                for _l in _r.splitlines():
                    _l = _l.strip()

                    if '_share_printers' in _l:
                        result['printer_sharing_enabled'] = '1' in _l

                    if 'WebInterface' in _l:
                        result['cups_web_interface_enabled'] = 'Yes' in _l

        return result

    def _sip_status(self):
        """SIP Status."""
        result = {'sip_enabled': ''}

        _cmd = ['/usr/bin/csrutil', 'status']

        _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _r, _e = _p.communicate()

        if _p.returncode == 0:
            if _r:
                if isinstance(_r, bytes):
                    _r = _r.decode('utf-8').strip()

                result['sip_enabled'] = 'System Integrity Protection status: enabled' in _r

        return result

    def _systemsetup(self):
        """System Setup."""
        result = {'ntp_enabled': '',
                  'ntp_servers': '',
                  'remote_apple_events_enabled': '',
                  'ssh_enabled': '',
                  'timezone': '',
                  'wake_on_lan': ''}

        _verbs = {'gettimezone': 'timezone',
                  'getusingnetworktime': 'ntp_enabled',
                  'getwakeonnetworkaccess': 'wake_on_lan',
                  'getremotelogin': 'ssh_enabled',
                  'getremoteappleevents': 'remote_apple_events_enabled'}

        # The '-getnetworktimeserver' systemsetup argument only returns the first
        # ntp server found in the '/etc/ntp.conf' file, so read it directly if it exists.
        _ntp_servers = list()
        _ntp_conf = '/etc/ntp.conf'

        if os.path.exists(_ntp_conf):
            with open(_ntp_conf, 'r') as _f:
                _lines = _f.readlines()

                if _lines:
                    for _l in _lines:
                        _srv = _l.strip().replace('server ', '')

                        # Maintain the order of servers read, and exclude duplicates
                        if _srv not in _ntp_servers:
                            _ntp_servers.append(_l.strip().replace('server ', ''))

        # Use 'systemsetup' for simple system details
        for _k, _v in _verbs.items():
            _cmd = ['/usr/sbin/systemsetup', '-{}'.format(_k)]

            _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _r, _e = _p.communicate()

            if _p.returncode == 0:
                if _r:
                    if isinstance(_r, bytes):
                        _r = _r.decode('utf-8').strip()

                    if _k not in ['gettimezone', 'getnetworktimeserver']:
                        result[_v] = 'On' in _r.split(': ')[1:]
                    elif _k == 'gettimezone':
                        result[_v] = _r.split(': ')[1]

        result['ntp_servers'] = _ntp_servers

        return result

    def _rosetta2_state(self):
        """Rosetta 2 state."""
        result = {'rosetta2_installed': False}

        # After macOS 11.4, path prefix appears to have changed
        if common.os_version() > common.vers_convert('11.4'):
            _rosetta_prefix = '/usr/libexec/rosetta'
        else:
            _rosetta_prefix = '/Library/Apple/usr/libexec/oah'

        _file_checks = ['oahd',
                        'oahd-helper',
                        'oahd-root-helper']

        result['rosetta2_installed'] = all([Path(_rosetta_prefix).joinpath(_f).exists() for _f in _file_checks])

        return result

    def _rosetta2_version(self, bundle_id='com.apple.pkg.RosettaUpdateAuto'):
        """Rosetta 2 version."""
        result = {'rosetta2_version': ''}
        _ver = ''

        _cmd = ['/usr/sbin/pkgutil', '--pkg-info-plist', bundle_id]

        _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _r, _e = _p.communicate()

        if _p.returncode == 0:
            if _r:
                try:
                    _ver = plist.readPlistFromString(obj=_r)['pkg-version']
                except KeyError:
                    pass

                result['rosetta2_version'] = _ver

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._ard_state())
        result.update(self._efi_password_state())
        result.update(self._printer_state())
        result.update(self._sip_status())
        result.update(self._systemsetup())
        result.update(self._rosetta2_state())
        result.update(self._rosetta2_version())

        return result


def runner(dest):
    se = SystemSetupConditions()
    mc = worker.MunkiConWorker(conditions_file=dest, log_src=__file__)

    mc.write(conditions=se.conditions)
