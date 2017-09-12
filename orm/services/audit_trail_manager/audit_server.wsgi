from pecan.deploy import deploy
from orm.base_config import ranger_base
application = deploy(ranger_base+'/orm/services/audit_trail_manager/config.py')
