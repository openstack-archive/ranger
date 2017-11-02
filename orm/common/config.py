#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
Configuration options registration.
"""

from oslo_config import cfg
from oslo_log import log as logging

CONF = cfg.CONF

api_opts = [
    cfg.HostAddressOpt(
        'host',
        default='0.0.0.0',
        help='Ranger API server host'
    ),
    cfg.BoolOpt('ssl_verify', default=False, help='Enable HTTPS')
]

db_opts = [
    cfg.HostAddressOpt('host', default='0.0.0.0', help='Ranger database host'),
    cfg.PortOpt('port', default=3306, help='Ranger database port'),
    cfg.StrOpt('user', default='root', help='Ranger database user'),
    cfg.StrOpt('password', default='stackdb', help='Ranger database password')
]

uuid_opts = [
    cfg.PortOpt('port', default=7001, help='uuid server port'),

]

API_GROUP = 'api'
DB_GROUP = 'db'
UUID_GROUP = 'uuid'


CONF.register_opts(api_opts, group=API_GROUP)
CONF.register_opts(uuid_opts, group=UUID_GROUP)
CONF.register_opts(db_opts, group=DB_GROUP)

logging.register_options(CONF)
logging.setup(CONF, 'ranger')

def parse_args(args=None):

    CONF(
        args=args,
        project='ranger',
        default_config_files=[]
    )
