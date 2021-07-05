import argparse
import logging
import logging.handlers
import plistlib

from os import geteuid, remove
from sys import exit, stderr
from pathlib import Path

VERSION = '1.0.20210705'

_ARGS = {
    'certificates': {'args': ['--certificates'],
                     'kwargs': {'action': 'store_true',
                                'dest': 'certificates',
                                'required': False,
                                'help': 'process certificate conditions from system keychain'}},
    'filevault': {'args': ['--filevault'],
                  'kwargs': {'action': 'store_true',
                             'dest': 'filevault',
                             'required': False,
                             'help': 'process FileVault conditions'}},
    'kext': {'args': ['--kexts'],
             'kwargs': {'action': 'store_true',
                        'dest': 'kext',
                        'required': False,
                        'help': 'process kext conditions'}},
    'mdm_enrolled': {'args': ['--mdm-enrolled'],
                     'kwargs': {'action': 'store_true',
                                'dest': 'mdm_enrolled',
                                'required': False,
                                'help': 'process MDM enrolled conditions'}},
    'pppcp': {'args': ['--pppcp'],
              'kwargs': {'action': 'store_true',
                         'dest': 'pppcp',
                         'required': False,
                         'help': 'process PPPCP conditions'}},
    'profiles': {'args': ['--profiles'],
                 'kwargs': {'action': 'store_true',
                            'dest': 'profiles',
                            'required': False,
                            'help': 'process profiles conditions'}},
    'python': {'args': ['--python'],
               'kwargs': {'action': 'store_true',
                          'dest': 'python',
                          'required': False,
                          'help': 'process python conditions'}},
    'system_extensions': {'args': ['--system-exts'],
                          'kwargs': {'action': 'store_true',
                                     'dest': 'system_extensions',
                                     'required': False,
                                     'help': 'process system extension conditions'}},
    'system_setup': {'args': ['--system-setup'],
                     'kwargs': {'action': 'store_true',
                                'dest': 'system_setup',
                                'required': False,
                                'help': 'process sytem setup conditions'}},
    'user_accounts': {'args': ['--user-accts'],
                      'kwargs': {'action': 'store_true',
                                 'dest': 'user_accounts',
                                 'required': False,
                                 'help': 'process user account conditions'}},
}


def arguments():
    result = None

    _parser = argparse.ArgumentParser()

    for _k, _arg in _ARGS.items():
        _parser.add_argument(*_arg['args'], **_arg['kwargs'])

    _parser.add_argument('--purge',
                         action='store_true',
                         dest='purge',
                         required=False,
                         help='purges all existing information')

    _parser.add_argument('--dest',
                         dest='destination',
                         required=False,
                         metavar='[path]',
                         help='output conditions to specific destination plist')

    _parser.add_argument('-v, --version',
                         action='version',
                         version='munkicon {}, Copyright 2020. Apache License V2.0'.format(VERSION))

    result = _parser.parse_args()

    return result


def main():
    CONDITIONS_FILE = '/Library/Managed Installs/ConditionalItems.plist'
    PREFS_FILE = '/Library/Preferences/com.github.carlashley.munkicon.plist'

    MODULES = ['certificates',
               'filevault',
               'kext',
               'mdm_enrolled',
               'pppcp',
               'profiles',
               'python',
               'system_extensions',
               'system_setup',
               'user_accounts']

    _args = arguments()

    if not geteuid() == 0:
        _msg = 'You must be root to run this tool.'
        print('{}'.format(_msg), file=stderr)
        exit(1)

    _process = {_k: _v for _k, _v in _args.__dict__.items() if _k in MODULES}

    log_path = '/Library/Logs/munkicon.log'
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    fh = logging.handlers.RotatingFileHandler(log_path, maxBytes=(1048576 * 10), backupCount=7)
    fmt = logging.Formatter("%(asctime)s - %(name)s -  %(levelname)s - %(message)s")
    fmt = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    fh.setFormatter(fmt)
    log.addHandler(fh)

    logging.getLogger(__name__).addHandler(logging.NullHandler())

    LOG = logging.getLogger(__name__)

    if _args.destination:
        CONDITIONS_FILE = _args.destination

    if _args.purge:
        if Path(CONDITIONS_FILE).exists():
            LOG.info('Removed condition file %s' % CONDITIONS_FILE)
            remove(CONDITIONS_FILE)

    # Import the processors after setting up.
    from . import certificates  # NOQA
    from . import filevault  # NOQA
    from . import kext  # NOQA
    from . import mdm_enrolled  # NOQA
    from . import pppcp  # NOQA
    from . import profiles  # NOQA
    from . import python  # NOQA
    from . import system_extensions  # NOQA
    from . import system_setup  # NOQA
    from . import user_accounts  # NOQA

    LOG.info('Writing conditions to %s' % CONDITIONS_FILE)

    # If no command line arguments are provided, process a preferences file
    # for processors to run, otherwise presume all processors are to be run.
    if not any([_run for _module, _run in _process.items()]):
        if Path(PREFS_FILE).exists():
            LOG.info('Processing conditions from preferences %s' % PREFS_FILE)
            with Path(PREFS_FILE).open('rb') as _f:
                _process = plistlib.load(_f)
        else:
            _process = {_k: True for _k in MODULES}

    LOG.debug('Conditions to process: %s' % _process)

    for _module, _run in _process.items():
        if _run:
            try:
                _condition = globals()[_module]
                try:
                    _condition.runner(dest=CONDITIONS_FILE)
                except AttributeError as e:
                    LOG.error(e)
                    pass
            except KeyError as e:
                LOG.error('No condition %s found' % e)
                pass
