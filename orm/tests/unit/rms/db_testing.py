import logging

from rms.storage.base_data_manager import SQLDBError
from rms.storage.my_sql.data_manager import DataManager

logger = logging.getLogger(__name__)


def run_db_tests(data_manager):
    logger.info('In db testing')

    try:
        # add regions with meta_data and end_points

        # end_point_list = [{"type": "ord", "url": "http://ord.com", "description": "ord url"},
        #                   {"type": "identity", "url": "http://identity.com", "description": "keystone url"},
        #                   {"type": "image", "url": "http://image.com", "description": "image api url"}]
        #
        # meta_data_list = [{"key": "key_1", "value": "value_1", "description": "meta data key 1"},
        #                   {"key": "key_2", "value": "value_2", "description": "meta data key 2"},
        #                   {"key": "key_3", "value": "value_3", "description": "meta data key 3"}]
        #
        # data_manager.add_region("region_1","region 1", "US", "Cal", "LA", "blv_1", "12345", 1,
        #                         "functional", "ranger_agent 1.0", "kilo", "dt_1", "lt_1",
        #                         "vlcp_1", "clli_1", "test test test", end_point_list, meta_data_list)
        #
        # data_manager.add_region("region_2","region 2", "IL", "IL", "TelAviv", "bazel 1", "12345", 0,
        #                         "functional", "ranger_agent 1.0", "kilo", "dt_1", "lt_1",
        #                         "vlcp_1", "clli_1", "test2 test2 test2", end_point_list, meta_data_list)
        #
        # # get all regions
        # regions = data_manager.get_all_regions()
        # logger.info(regions)

        # region_dict = {"address_country":"Cal"}
        # meta_data_dict = {"meta_data_key": "key_1", "meta_data_value": "value_1"}
        # end_point_dict = None#{"end_point_type": "type_1"}
        # x = data_manager.get_regions(region_dict,
        #                           meta_data_dict,
        #                           end_point_dict)

        # delete exist region
        # data_manager.delete_region("region_1")

        # delete a region that does not exist
        # data_manager.delete_region("region_25")

        # remove valid meta_data entry from a region
        # data_manager.remove_meta_data_from_region("region_2","key_1")

        # remove invalid meta_data entry from a region
        # data_manager.remove_meta_data_from_region("region_6", "key_999")

        # add meta_data to valid region
        # data_manager.add_meta_data_to_region("region_2","b_key", "b_value", "bla bla")

        # add meta_data to invalid region
        # data_manager.add_meta_data_to_region("region_7", "c_key", "c_value", "cla cla")

        # add end_point to valid region
        # data_manager.add_end_point_to_region("region_2","type_c", "url_c", "cla cla")
        # data_manager.add_end_point_to_region("region_6", "type_c", "url_ccc", "cla cla")

        # add end_point to invalid region
        # data_manager.add_end_point_to_region("region_7", "type_7", "url_7", "cla7 cla7")

        # x = data_manager.get_all_regions()
        # logger.info(x)

        # data_manager.add_group("group_0","group 0 description",["lcp_1", "lcp_2"])
        # data_manager.delete_group("group_0")
        # data_manager.remove_region_from_group("group_0","lcp_1")
        # data_manager.add_region_to_group("group_0","lcp_0")
        # data_manager.add_group("group_1","group 1","group 1 description",["SNA1","SNA2"])
        # data_manager.get_all_groups()
        x = data_manager.get_group("group_1")
        logger.info(x)
    except SQLDBError as e:
        logger.error("SQL error raised {}".format(e.message))


def main():
    db_url = 'mysql://root:stack@127.0.0.1/orm_rms_db?charset=utf8'

    data_manager = DataManager(db_url)

    run_db_tests(data_manager)

if __name__ == "__main__":
    main()
