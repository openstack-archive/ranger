import pecan
import logging

from pecan import rest

LOG = logging.getLogger(__name__)


class LcpController(rest.RestController):
    """
       this class is for getting the lcp list from AIC Formation.
    """

    @pecan.expose()
    def get(self):
        """
        when a get call is received in RestAPI this function return a
        list of lcp
        """
        LOG.info('int get function')

        file = open('data/zones.json', 'r')
        zones = file.read()

        # return the lcp's as dictionary so they can be converted to Json
        return zones
