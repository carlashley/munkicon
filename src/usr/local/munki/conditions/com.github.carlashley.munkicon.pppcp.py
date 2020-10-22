#!/usr/local/munki/python
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
                        _ae_rec_identity = None
                        _tcc_type = _ktcc_map[_k]

                        # Apple Events has a deeper nesting structure.
                        if _k == 'kTCCServiceAppleEvents':
                            _v = _v.get(_item)

                            _ae_rec_identity = _v.get('AEReceiverIdentifier', None)

                        _identifier = _v.get('Identifier', None)

                        # macOS 11+ introduces replacement of bool 'Allowed' with 'Authorization'
                        # which has three values: 'Allow', 'Deny', 'AllowStandardUserToSetSystemService'
                        # So look for 'Authorization' first then check for the bool 'Allowed' and if
                        # 'Allowed' is present, map back the bool to 'Allow' for 'True' and 'Deny'
                        # for 'False'.
                        try:
                            _auth = _v['Authorization']

                            # Make the 'AllowStandardUserToSetSystemService' a little easier to type
                            # in munki conditionals statements.
                            if _auth == 'AllowStandardUserToSetSystemService':
                                _auth = 'allow_standard_user'
                        except KeyError:
                            _auth = 'Allow' if _v['Allowed'] else 'Deny'

                        # Only add if there's an identifier
                        if _identifier:
                            _tcc_str = '{},{}'.format(_auth.lower(), _identifier)

                            if _ae_rec_identity:
                                _tcc_str = '{},{}'.format(_tcc_str, _ae_rec_identity)

                            if _tcc_str not in result[_tcc_type]:
                                result[_tcc_type].append(_tcc_str)

        return result

    def _process(self):
        """Process all conditions and generate the condition dictionary."""
        result = dict()

        result.update(self._pppcp_overrides())

        return result


def main():
    pppcp = PPPCPConditions()
    mc = worker.MunkiConWorker(log_src=__file__)

    mc.write(conditions=pppcp.conditions)


if __name__ == '__main__':
    main()
