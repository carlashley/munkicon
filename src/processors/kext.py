import os
import sqlite3



try:
    from munkicon import worker
except ImportError:
    from .munkicon import worker

# Keys: 'kext_teams'
#       'kext_bundles'
#       'kext_team_bundle'


class SQLiteDB():
    """SQLite"""
    def __init__(self, db='/var/db/SystemPolicyConfiguration/KextPolicy'):
        self._db = db
        self._connection = None

        self.cursor = None

    def _connect(self):
        """Connect."""
        self._connection = sqlite3.connect(self._db)

        self.cursor = self._connection.cursor()

    def _disconnect(self):
        """Disconnect."""
        self._connection.close()

    def query(self, q):
        """Query. Fetch all."""
        result = None

        if os.path.exists(self._db):
            self._connect()

            try:
                self.cursor.execute(q)

                _columns = [_desc[0] for _desc in self.cursor.description]
                _rows = list()

                for _r in self.cursor.fetchall():
                    _row = {_key: _value for _key, _value in zip(_columns, _r)}

                    _rows.append(self.Row(**_row))

                result = _rows
            except Exception:
                self._disconnect()
                raise
        return result

    class Row(object):
        def __init__(self, **kwargs):
            for _k, _v in kwargs.items():
                setattr(self, _k, _v)


class KextPolicyConditions(object):
    """Whitelisted KEXT's as applied by MDM or set by user."""
    def __init__(self):
        self._mdm_query = 'SELECT team_id, bundle_id, allowed FROM kext_policy_mdm'
        self._usr_query = 'SELECT team_id, bundle_id, allowed FROM kext_policy'
        self._db = SQLiteDB()

        self.conditions = self._process()

    def _teams(self):
        """Team ID's"""
        result = {'kext_teams': list()}

        _mdm = {_x.team_id for _x in self._db.query(q=self._mdm_query)}
        _usr = {_x.team_id for _x in self._db.query(q=self._usr_query)}

        result['kext_teams'] = list(_mdm.union(_usr))

        return result

    def _bundles(self):
        """Bundle ID's"""
        result = {'kext_bundles': list()}

        _mdm = {_x.bundle_id for _x in self._db.query(q=self._mdm_query)}
        _usr = {_x.bundle_id for _x in self._db.query(q=self._usr_query)}

        result['kext_bundles'] = list(_mdm.union(_usr))

        return result

    def _team_bundles(self):
        """Team & Bundle ID's"""
        result = {'kext_bundles': list()}

        _mdm = {'{},{}'.format(_x.team_id, _x.bundle_id) for _x in self._db.query(q=self._mdm_query)}
        _usr = {'{},{}'.format(_x.team_id, _x.bundle_id) for _x in self._db.query(q=self._usr_query)}

        result['kext_team_bundles'] = list(_mdm.union(_usr))

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._teams())
        result.update(self._bundles())
        result.update(self._team_bundles())

        return result


def runner(dest):
    kext = KextPolicyConditions()
    mc = worker.MunkiConWorker(conditions_file=dest, log_src=__file__)

    mc.write(conditions=kext.conditions)
