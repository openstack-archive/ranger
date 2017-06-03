import logging
import csv

from rms.storage.base_data_manager import SQLDBError

from rms.storage.my_sql.data_manager import DataManager
import config

logger = logging.getLogger(__name__)


def load_csv2db(data_manager):
    logger.info('Loading csv to db..')

    try:

        with open('rms/resources/regions.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                end_point_list = [{"type": "ord",
                                   "url": row["ord_url"]
                                   },
                                  {"type": "dashboard",
                                   "url": row["horizon_url"],
                                   },
                                  {"type": "identity",
                                   "url": row["keystone_url"],
                                   }]
                data_manager.add_region(row["region_id"],
                                        row["region_name"],
                                        row["address_state"],
                                        row["address_country"],
                                        row["address_city"],
                                        row["address_street"],
                                        row["address_zip"],
                                        row["region_status"],
                                        row["ranger_agent_version"],
                                        row["open_stack_version"],
                                        row["location_type"],
                                        row["vlcp_name"],
                                        row["clli"],
                                        row["design_type"],
                                        end_point_list,
                                        None,
                                        row["description"])

    except SQLDBError as e:
        logger.error("SQL error raised {}".format(e.message))


def main():
    db_url = config.database['url']
    data_manager = DataManager(db_url, 3, 3)
    load_csv2db(data_manager)

if __name__ == "__main__":
    main()
