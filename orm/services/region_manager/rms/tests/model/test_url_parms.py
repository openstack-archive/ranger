"""url parms unittests module."""
import unittest

from rms.model import url_parm

parms = {'status': 'functional', 'city': 'Los Angeles', 'clli': 'clli_0',
         'zip': '012345', 'country': 'US', 'metadata': ['key_1:value_1',
                                                        'key_2:value_2'],
         'valet': 'true', 'state': 'Cal', 'street': 'Blv st',
         'rangerAgentVersion': 'ranger_agent 1.0', 'osversion': 'kilo',
         'type': 'location_type_0', 'regionname': 'lcp 0'}

parms_meta_none = {'status': 'functional', 'city': 'Los Angeles',
                   'clli': 'clli_0',
                   'zip': '012345', 'country': 'US',
                   'metadata': None,
                   'valet': 'true', 'state': 'Cal', 'street': 'Blv st',
                   'rangerAgentVersion': 'ranger_agent 1.0', 'osversion': 'kilo',
                   'type': 'location_type_0', 'regionname': 'lcp 0'}

output_parms = {'address_city': 'Los Angeles', 'clli': 'clli_0',
                'name': 'lcp 0', 'open_stack_version': 'kilo',
                'address_street': 'Blv st', 'address_state': 'Cal',
                'region_status': 'functional', 'valet': 'true',
                'ranger_agent_version': 'ranger_agent 1.0', 'address_zip': '012345',
                'address_country': 'US', 'location_type': 'location_type_0',
                'metadata': ['key_1:value_1', 'key_2:value_2']}

regiondict_output = {'address_city': 'Los Angeles', 'clli': 'clli_0',
                     'name': 'lcp 0', 'valet': 'true',
                     'open_stack_version': 'kilo', 'address_country': 'US',
                     'ranger_agent_version': 'ranger_agent 1.0', 'region_status': 'functional',
                     'address_state': 'Cal', 'address_street': 'Blv st',
                     'location_type': 'location_type_0',
                     'address_zip': '012345'}
metadata_output = {'meta_data_keys': [],
                   'meta_data_pairs': [{'metadata_key': 'key_1', 'metadata_value': 'value_1'},
                                       {'metadata_key': 'key_2', 'metadata_value': 'value_2'}],
                   'ref_keys': ['key_1', 'key_2']}


class TestUrlParms(unittest.TestCase):
    # parms init
    def test_init_all(self):
        obj = url_parm.UrlParms(**parms)
        self.assertEqual(obj.__dict__, output_parms)

    # test build query
    def test_build_query(self):
        obj = url_parm.UrlParms(**parms)
        regiondict, metadatadict, none = obj._build_query()
        self.assertEqual(regiondict_output, regiondict)
        self.assertEqual(metadata_output, metadatadict)

    # test build query metadat None
    def test_build_query_meta_none(self):
        obj = url_parm.UrlParms(**parms_meta_none)
        regiondict, metadatadict, none = obj._build_query()
        self.assertEqual(metadatadict, None)

    # test build query metadat None
    def test_build_query_all_none(self):
        obj = url_parm.UrlParms()
        regiondict, metadatadict, none = obj._build_query()
        self.assertEqual(metadatadict, None)
        self.assertEqual(regiondict, None)
