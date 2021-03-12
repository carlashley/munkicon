import os



try:
    from munkicon import plist
    from munkicon import worker
except ImportError:
    from .munkicon import plist
    from .munkicon import worker

# Keys: 'tcc_accessibility'
#       'tcc_address_book'
#       'tcc_apple_events'
#       'tcc_calendar'
#       'tcc_camera'
#       'tcc_file_provider_presence'
#       'tcc_listen_event'
#       'tcc_media_library'
#       'tcc_microphone'
#       'tcc_photos'
#       'tcc_post_event'
#       'tcc_reminders'
#       'tcc_screen_capture'
#       'tcc_speech_recognition'
#       'tcc_all_files'
#       'tcc_desktop_folder'
#       'tcc_documents_folder'
#       'tcc_downloads_folder'
#       'tcc_network_volumes'
#       'tcc_removable_volumes'
#       'tcc_sys_admin_files'


class PPPCPConditions(object):
    """PPPCP Profiles"""
    def __init__(self):
        self.conditions = self._process()

    def _parse_item(self, obj):
        """Parse PPPCP object."""
        result = {'ae_identifier': obj.get('AEReceiverIdentifier', None),
                  'identifier': obj.get('Identifier', None),
                  'auth': None}
        # macOS 11+ introduces replacement of bool 'Allowed' with 'Authorization'
        # which has three values: 'Allow', 'Deny', 'AllowStandardUserToSetSystemService'
        # So look for 'Authorization' first then check for the bool 'Allowed' and if
        # 'Allowed' is present, map back the bool to 'Allow' for 'True' and 'Deny'
        # for 'False'.
        try:
            _auth = obj['Authorization']
        except KeyError:
            _auth = 'Allow' if obj['Allowed'] else 'Deny'

        # Make the 'AllowStandardUserToSetSystemService' a little easier to type
        # in munki conditionals statements.
        if _auth == 'AllowStandardUserToSetSystemService':
            _auth = 'allow_standard_user'

        result['auth'] = _auth.lower()

        return result

    def _pppcp_overrides(self):
        """Returns PPPCP identifiers from MDM overrides."""
        result = dict()

        # TCC Map
        _ktcc_map = {'kTCCServiceAccessibility': 'tcc_accessibility',
                     'kTCCServiceAddressBook': 'tcc_address_book',
                     'kTCCServiceAppleEvents': 'tcc_apple_events',
                     'kTCCServiceCalendar': 'tcc_calendar',
                     'kTCCServiceCamera': 'tcc_camera',
                     'kTCCServiceFileProviderPresence': 'tcc_file_provider_presence',
                     'kTCCServiceListenEvent': 'tcc_listen_event',
                     'kTCCServiceMediaLibrary': 'tcc_media_library',
                     'kTCCServiceMicrophone': 'tcc_microphone',
                     'kTCCServicePhotos': 'tcc_photos',
                     'kTCCServicePostEvent': 'tcc_post_event',
                     'kTCCServiceReminders': 'tcc_reminders',
                     'kTCCServiceScreenCapture': 'tcc_screen_capture',
                     'kTCCServiceSpeechRecognition': 'tcc_speech_recognition',
                     'kTCCServiceSystemPolicyAllFiles': 'tcc_all_files',
                     'kTCCServiceSystemPolicyDesktopFolder': 'tcc_desktop_folder',
                     'kTCCServiceSystemPolicyDocumentsFolder': 'tcc_documents_folder',
                     'kTCCServiceSystemPolicyDownloadsFolder': 'tcc_downloads_folder',
                     'kTCCServiceSystemPolicyNetworkVolumes': 'tcc_network_volumes',
                     'kTCCServiceSystemPolicyRemovableVolumes': 'tcc_removable_volumes',
                     'kTCCServiceSystemPolicySysAdminFiles': 'tcc_sys_admin_files'}

        # Generate the results keys to return.
        for _k, _v in _ktcc_map.items():
            result[_v] = list()

        _mdmoverrides = '/Library/Application Support/com.apple.TCC/MDMOverrides.plist'

        if os.path.exists(_mdmoverrides):
            _overrides = plist.readPlist(path=_mdmoverrides)

            if _overrides:
                for _item, _payload in _overrides.items():
                    for _k, _v in _payload.items():
                        _tcc_type = _ktcc_map[_k]

                        # Apple Events has a deeper nesting structure.
                        if _k == 'kTCCServiceAppleEvents':
                            # There might be multiple dictionaries in the value for 'kTCCServiceAppleEvents'
                            # I really hope not :|
                            for _id, _vals in _v.items():
                                _entry = self._parse_item(_vals)
                                _ae_id = _entry.get('ae_identifier', None)
                                _auth = _entry.get('auth', None)
                                _id = _entry.get('identifier', None)

                                # Only add if there's an identifier
                                if _ae_id and _auth and _id:
                                    _tcc_str = '{},{},{}'.format(_auth, _id, _ae_id)

                                    if _tcc_str not in result[_tcc_type]:
                                        result[_tcc_type].append(_tcc_str)
                        else:
                            _entry = self._parse_item(_v)
                            _ae_id = _entry.get('ae_identifier', None)
                            _auth = _entry.get('auth', None)
                            _id = _entry.get('identifier', None)

                            # Only add if there's an identifier
                            if _auth and _id:
                                _tcc_str = '{},{},{}'.format(_auth, _id, _ae_id)

                                if _tcc_str not in result[_tcc_type]:
                                    result[_tcc_type].append(_tcc_str)

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._pppcp_overrides())

        return result


def runner(dest):
    pppcp = PPPCPConditions()
    mc = worker.MunkiConWorker(conditions_file=dest, log_src=__file__)

    mc.write(conditions=pppcp.conditions)
