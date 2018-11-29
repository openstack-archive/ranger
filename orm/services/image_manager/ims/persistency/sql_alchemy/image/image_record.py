from orm.services.image_manager.ims.logger import get_logger
from orm.services.image_manager.ims.persistency.sql_alchemy.db_models import (Image, ImageCustomer,
                                                                              ImageRegion)
from orm.services.image_manager.ims.persistency.sql_alchemy.infra.record import Record

LOG = get_logger(__name__)


class ImageRecord(Record):
    def __init__(self, session):

        # this model is uses only for the parameters of access mothods, not an instance of model in the database
        self.__image = Image()
        # self.set_record_data(self.__image)
        # self.__image.clear()
        Record.__init__(self)
        self.__image = None
        self.__TableName = "image"

        if session:
            self.set_db_session(session)

    @property
    def image(self):
        return self.__image

    @image.setter
    def image(self, image):
        self.__image = image

    def insert(self, image):
        try:
            self.session.add(image)
        except Exception as exception:
            LOG.log_exception("Failed to insert image" + str(image), exception)
            # LOG.error("Failed to insert image" + str(image) + " Exception:" + str(exception))
            raise

    def get_image(self, id):
        """function to get image by name or id"""
        try:
            query = self.session.query(Image).filter((Image.id == id) | (Image.name == id))
            return query.first()
        except Exception as exception:
            message = "Failed to read_image:  id: {0}".format(id)
            LOG.log_exception(message, exception)
            raise

    def delete_image_by_id(self, id):
        try:
            result = self.session.connection().execute("delete from image where id = '{0}'".format(id))  #nosec
            return result

        except Exception as exception:
            message = "Failed to delete_by_internal_id: internal_id: {0}".format(id)
            LOG.log_exception(message, exception)
            raise

    def create_images_by_name_query(self, name):
        try:
            query = self.session.query(Image).filter(Image.name == name)
            return query
        except Exception as exception:
            message = "Failed to create_images_by_name_query:  name: {0}".format(name)
            LOG.log_exception(message, exception)
            raise

    def get_images_by_name(self, name, **kw):
        try:
            query = self.create_images_by_name_query(name)
            query = self.customise_query(query, kw)
            return query.all()
        except Exception as exception:
            message = "Failed to get_images_by_name:  name: {0}".format(name)
            LOG.log_exception(message, exception)
            raise

    def get_image_by_id(self, id):
        try:
            image = self.session.query(Image).filter(Image.id == id)
            return image.first()

        except Exception as exception:
            message = "Failed to get_image_by_id: id: {0}".format(id)
            LOG.log_exception(message, exception)
            raise

    def get_count_of_images_by_name(self, name):
        try:
            query = self.create_images_by_name_query(name)
            return query.count()
        except Exception as exception:
            message = "Failed to get_images_by_name_count:  name: {0}".format(name)
            LOG.log_exception(message, exception)
            raise

    def get_images_status_by_uuids(self, uuid_str):
        results = self.session.connection().execute("SELECT id, resource_id, region, status"  #nosec
                                                    "  FROM rds_resource_status_view WHERE resource_id IN ({})".format(uuid_str))
        img_region_dict = {}
        if results:
            resource_status_dict = dict((id, (resource_id, region, status)) for id, resource_id, region, status in results)
            # using resource_status_dict, create img_region_dict with resource_id as key and (region, status) as value
            for v in resource_status_dict.values():
                if v[0] in img_region_dict:
                    img_region_dict[v[0]].append(v[1:])
                else:
                    img_region_dict[v[0]] = [v[1:]]
            results.close()
        return img_region_dict

    def create_images_by_visibility_query(self, visibility):
        try:
            query = self.session.query(Image).filter(Image.visibility == visibility)
            return query
        except Exception as exception:
            message = "Failed to create_images_by_visibility_query:  visibility: {0}".format(visibility)
            LOG.log_exception(message, exception)
            raise

    def get_images_by_visibility(self, visibility, **kw):
        try:
            query = self.create_images_by_visibility_query(visibility)
            query = self.customise_query(query, kw)
            return query.all()
        except Exception as exception:
            message = "Failed to get_images_by_visibility:  visibility: {0}".format(visibility)
            LOG.log_exception(message, exception)
            raise

    def get_count_of_images_by_visibility(self, visibility):
        try:
            query = self.create_images_by_visibility_query(visibility)
            return query.count()
        except Exception as exception:
            message = "Failed to get_images_by_visibility_count:  visibility: {0}".format(visibility)
            LOG.log_exception(message, exception)
            raise

    def create_all_images_query(self):
        try:
            query = self.session.query(Image).filter()
            return query
        except Exception as exception:
            message = "Failed to create_all_images_query: ".format()
            LOG.log_exception(message, exception)
            raise

    def get_all_images(self, **kw):
        try:
            query = self.create_all_images_query()
            query = self.customise_query(query, kw)
            return query.all()
        except Exception as exception:
            message = "Failed to get_all_images: ".format()
            LOG.log_exception(message, exception)
            raise

    def get_count_of_all_images(self):
        try:
            query = self.create_all_images_query()
            return query.count()
        except Exception as exception:
            message = "Failed to get_all_images_count: ".format()
            LOG.log_exception(message, exception)
            raise

    def get_images_by_criteria(self, **criteria):
        try:
            LOG.debug("get_images_by_criteria: criteria: {0}".format(criteria))
            visibility = criteria[
                'visibility'] if 'visibility' in criteria else None
            region = criteria['region'] if 'region' in criteria else None
            Customer = criteria['Customer'] if 'Customer' in criteria else None

            query = self.session.query(Image)

            if region:
                query = query.join(ImageRegion).filter(
                    ImageRegion.image_id == Image.id,
                    ImageRegion.region_name == region)
            if Customer:
                query = query.join(ImageCustomer).filter(
                    ImageCustomer.image_id == Image.id,
                    ImageCustomer.customer_id == Customer)
            if visibility:
                query = query.filter(Image.visibility == visibility)

            query = self.customise_query(query, criteria)
            return query.all()

        except Exception as exception:
            message = "Failed to get_images_by_criteria: criteria: {0}".format(
                criteria)
            LOG.log_exception(message, exception)
            raise
