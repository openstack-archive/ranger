from pecan.deploy import deploy
from orm.base_config import ranger_base
application = deploy(ranger_base+'/orm/services/resource_distributor/config.py')
