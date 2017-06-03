import logging
import csv

from rms.storage.base_data_manager import SQLDBError

from rms.storage.my_sql.data_manager import DataManager
import config

logger = logging.getLogger(__name__)


def revert_csv2db(data_manager):
    logger.info('revert csv to db..')

    try:

        with open('rms/resources/regions.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data_manager.delete_region(row["region_id"])

    except SQLDBError as e:
        logger.error("SQL error raised {}".format(e.message))


def main():
    db_url = config.database['url']
    data_manager = DataManager(db_url)
    revert_csv2db(data_manager)

if __name__ == "__main__":
    main()
