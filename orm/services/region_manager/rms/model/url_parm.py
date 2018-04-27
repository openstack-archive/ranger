"""module."""


class UrlParms(object):
    """class method."""

    def __init__(self, type=None, status=None, metadata=None, rangerAgentVersion=None,
                 clli=None, regionname=None, osversion=None, location_type=None,
                 state=None, country=None, city=None, street=None, zip=None,
                 vlcp_name=None):
        """init method.

        :param type:
        :param status:
        :param metadata:
        :param rangerAgentVersion:
        :param clli:
        :param regionname:
        :param osversion:
        :param location_type:
        :param state:
        :param country:
        :param city:
        :param street:
        :param zip:
        :param vlcp_name:
        """
        if type:
            self.design_type = type
        if status:
            self.region_status = status
        if metadata:
            self.metadata = metadata
        if rangerAgentVersion:
            self.ranger_agent_version = rangerAgentVersion
        if clli:
            self.clli = clli
        if regionname:
            self.name = regionname
        if osversion:
            self.open_stack_version = osversion
        if location_type:
            self.location_type = location_type
        if state:
            self.address_state = state
        if country:
            self.address_country = country
        if city:
            self.address_city = city
        if street:
            self.address_street = street
        if zip:
            self.address_zip = zip
        if vlcp_name:
            self.vlcp_name = vlcp_name

    def _build_query(self):
        """nuild db query.

        :return:
        """
        metadatadict = None
        regiondict = None
        if self.__dict__:
            metadatadict = self._build_metadata_dict()
            regiondict = self._build_region_dict()
        return regiondict, metadatadict, None

    def _build_metadata_dict(self):
        """meta_data dict.

        :return: metadata dict
        """
        metadata = None
        if 'metadata' in self.__dict__:
            metadata = {'ref_keys': [], 'meta_data_pairs': [],
                        'meta_data_keys': []}
            for metadata_item in self.metadata:
                if ':' in metadata_item:
                    key = metadata_item.split(':')[0]
                    metadata['ref_keys'].append(key)
                    metadata['meta_data_pairs'].\
                        append({'metadata_key': key,
                                'metadata_value': metadata_item.split(':')[1]})
                else:
                    metadata['meta_data_keys'].append(metadata_item)
            # Now clean irrelevant values
            keys_list = []
            for item in metadata['meta_data_keys']:
                if item not in metadata['ref_keys']:
                    keys_list.append(item)

            metadata['meta_data_keys'] = keys_list

        return metadata

    def _build_region_dict(self):
        """region dict.

        :return:regin dict
        """
        regiondict = {}
        for key, value in self.__dict__.items():
            if key != 'metadata':
                regiondict[key] = value
        return regiondict
