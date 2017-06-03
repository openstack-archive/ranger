
class BaseDataManager(object):

    def __init__(self, url,
                 max_retries,
                 retry_interval):
        pass

    def add_region(self,
                   region_id,
                   name,
                   address_state,
                   address_country,
                   address_city,
                   address_street,
                   address_zip,
                   region_status,
                   ranger_agent_version,
                   open_stack_version,
                   design_type,
                   location_type,
                   vlcp_name,
                   clli,
                   description,
                   meta_data_list,
                   end_point_list):
        raise NotImplementedError("Please Implement this method")

    """
    def delete_region(self,
                      region_id):
        raise NotImplementedError("Please Implement this method")
    """

    def get_regions(self,
                    region_filters_dict,
                    meta_data_dict,
                    end_point_dict):
        raise NotImplementedError("Please Implement this method")

    def get_all_regions(self):
        raise NotImplementedError("Please Implement this method")

    """
    def add_meta_data_to_region(self,
                                region_id,
                                key,
                                value,
                                description):
        raise NotImplementedError("Please Implement this method")

    def remove_meta_data_from_region(self,
                                     region_id,
                                     key):
        raise NotImplementedError("Please Implement this method")

    def add_end_point_to_region(self,
                                region_id,
                                end_point_type,
                                end_point_url,
                                description):
        raise NotImplementedError("Please Implement this method")

    def remove_end_point_from_region(self,
                                     region_id,
                                     end_point_type):
        raise NotImplementedError("Please Implement this method")
    """

    def add_group(self,
                  group_id,
                  group_name,
                  group_description,
                  region_ids_list):
        raise NotImplementedError("Please Implement this method")

    """
    def delete_group(self,
                     group_name):
        raise NotImplementedError("Please Implement this method")
    """

    def get_group(self, group_id):
        raise NotImplementedError("Please Implement this method")

    def get_all_groups(self):
        raise NotImplementedError("Please Implement this method")

    """
    def add_region_to_group(self,
                            group_id,
                            region_id):
        raise NotImplementedError("Please Implement this method")

    def remove_region_from_group(self,
                                 group_id,
                                 region_id):
        raise NotImplementedError("Please Implement this method")
    """


class SQLDBError(Exception):
    pass


class EntityNotFound(Exception):
    """if item not found in DB."""
    pass


class DuplicateEntryError(Exception):
    """A group already exists."""
    pass


class InputValueError(Exception):
    """ unvalid input from user"""
    pass
