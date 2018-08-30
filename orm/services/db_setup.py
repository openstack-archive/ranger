#!/usr/bin/env python
# Copyright (c) 2012 OpenStack Foundation
# All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

from oslo_config import cfg
from sqlalchemy import *
import codecs
import sys
import sqlparse

CONF = cfg.CONF
codecs.register(lambda name: codecs.lookup('utf8') if name == 'utf8mb4' else None)

def main(argv=None):

    if argv is None:
        argv = sys.argv
    cfg.CONF(argv[1:], project='ranger', validate_default_values=True)

    OrmOpts = [
        cfg.StrOpt('ranger_base',
                   default='/opt/stack/ranger',
                   help='Orm base directory.'),
    ]

    CONF.register_opts(OrmOpts)

    orm_database_group = cfg.OptGroup(name='database',
                                      title='Orm Database Options')
    OrmDatabaseGroup = [
        cfg.StrOpt('connection',
                   help='The SQLAlchemy connection string to use to connect to '
                        'the ORM database.',
                   secret=True),
        cfg.IntOpt('max_retries',
                   default=-1,
                   help='The maximum number of retries for database connection.')
    ]

    CONF.register_group(orm_database_group)
    CONF.register_opts(OrmDatabaseGroup, orm_database_group)

    sql_queries = []

    orm_dbs = [
        CONF.ranger_base + '/orm/services/audit_trail_manager/scripts/db_scripts/create_db.sql',
        CONF.ranger_base + '/orm/services/id_generator/scripts/db_scripts/db_create.sql',
        CONF.ranger_base + '/orm/services/resource_distributor/scripts/db_scripts/create_db.sql',
        CONF.ranger_base + '/orm/services/region_manager/scripts/db_scripts/create_db.sql',
        CONF.ranger_base +
        '/orm/services/customer_manager/scripts/db_scripts/ranger_cms_create_db.sql',
        CONF.ranger_base +
        '/orm/services/customer_manager/scripts/db_scripts/ranger_cms_update_db.sql',
        CONF.ranger_base +
        '/orm/services/flavor_manager/scripts/db_scripts/ranger_fms_create_db.sql',
        CONF.ranger_base + '/orm/services/image_manager/scripts/db_scripts/create_db.sql'
    ]

    for item in range(len(orm_dbs)):
        with open(orm_dbs[item], 'rb') as f:
            for statement in sqlparse.split(f.read()):
                if not statement:
                    continue
                print statement
                sql_queries.append(statement)

    engine = create_engine(CONF.database.connection, echo=False)

    for exec_item in range(len(sql_queries)):
        try:
            conn = engine.connect()
            exec_script = conn.execute(sql_queries[exec_item])
            conn.close()
        except Exception as e:
            print e
    print 'Ranger databases setup complete'
