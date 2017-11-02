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

uuid_opts = [
    cfg.PortOpt('port', default=7001, help='uuid server port'),

]

db_connection = cfg.StrOpt('connection', default='',
                           help='Ranger database connection string')

API_GROUP = 'api'
UUID_GROUP = 'uuid'
DB_GROUP = 'database'


CONF.register_opts(api_opts, group=API_GROUP)
CONF.register_opts(uuid_opts, group=UUID_GROUP)
CONF.register_opt(db_connection, group=DB_GROUP)

logging.register_options(CONF)


def parse_args(args=None):

    logging.setup(CONF, 'ranger')

    CONF(
        args=args,
        project='ranger',
        default_config_files=[]
    )
