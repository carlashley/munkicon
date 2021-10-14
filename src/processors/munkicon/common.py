import subprocess

from distutils.version import LooseVersion


def vers_convert(ver=None):
    """Convert a string into a LooseVersion object."""
    # NOTE: Return '0.0.0' if 'ver' is None because LooseVersion can't handle 'None'
    result = LooseVersion('0.0.0')

    if not isinstance(ver, LooseVersion):
        if isinstance(ver, str):
            result = LooseVersion(ver)
        elif isinstance(ver, (float, int)):
            result = LooseVersion(str(ver))
    elif isinstance(ver, LooseVersion):
        result = ver

    return result


def os_build():
    """macOS build"""
    result = None
    cmd = ['/usr/bin/sw_vers', '-buildVersion']
    _p = subprocess.run(cmd, capture_output=True, encoding='utf-8')

    if _p.returncode == 0:
        result = _p.stdout.strip()

    return result


def os_version():
    """macOS version number."""
    # Note: Software version "might" get reported as '10.16' depending on Python used.
    result = None
    cmd = ['/usr/bin/sw_vers', '-productVersion']
    _p = subprocess.run(cmd, capture_output=True, encoding='utf-8')

    if _p.returncode == 0:
        result = vers_convert(_p.stdout.strip())

    return result
