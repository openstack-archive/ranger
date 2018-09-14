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
import sys

CONF = cfg.CONF


def main(argv=None):

    if argv is None:
        argv = sys.argv
    cfg.CONF(argv[1:], project='ranger', validate_default_values=True)

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

    drop_db_stmt = "SET sql_notes = 0;" \
                   "DROP database orm;" \
                   "DROP database orm_audit;" \
                   "DROP database orm_cms_db;" \
                   "DROP database orm_fms_db;" \
                   "DROP database orm_rds;" \
                   "DROP database orm_rms_db;" \
                   "DROP database orm_uuidgen;"

    db_conn_url = CONF.database.connection
    db_conn_url = db_conn_url and db_conn_url.replace("mysql+pymysql", "mysql") or ''
    engine = create_engine(db_conn_url, echo=False)

    conn = engine.connect()
    exec_script = conn.execute(drop_db_stmt)
    conn.close()
