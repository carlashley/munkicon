import subprocess



try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker

# Keys: 'enrolled_via_dep'
#       'mdm_enrollment'


class MDMEnrolledConditions(object):
    def __init__(self):
        self.conditions = self._process()

    def _enrolled_state(self):
        """MDM/DEP Enrolled State."""
        result = {'enrolled_via_dep': '',
                  'mdm_enrollment': ''}

        _cmd = ['/usr/bin/profiles', 'status', '-type', 'enrollment']
        _p = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _r, _e = _p.communicate()

        if _p.returncode == 0:
            if isinstance(_r, bytes):
                _r = _r.decode('utf-8').strip()

            for _l in _r.splitlines():
                _l = _l.strip()

                if 'DEP' in _l:
                    result['enrolled_via_dep'] = _l.split(': ')[1].lower()

                if 'MDM enrollment' in _l:
                    result['mdm_enrollment'] = _l.split(': ')[1].lower()

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._enrolled_state())

        return result


def runner(dest):
    mdm = MDMEnrolledConditions()
    mc = worker.MunkiConWorker(conditions_file=dest, log_src=__file__)

    mc.write(conditions=mdm.conditions)
