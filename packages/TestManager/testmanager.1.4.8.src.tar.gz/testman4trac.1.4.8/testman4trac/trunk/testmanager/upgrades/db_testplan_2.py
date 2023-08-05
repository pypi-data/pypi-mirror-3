from trac.db import Table, Column, Index, DatabaseManager

from tracgenericclass.util import *

from testmanager.model import TestManagerModelProvider

def do_upgrade(env, ver, db_backend, db):
    """
    Add 'contains_all' and 'freeze_tc_versions' columns to testplan table
    """
    cursor = db.cursor()
    
    realm = 'testplan'
    cursor.execute("CREATE TEMPORARY TABLE %(realm)s_old AS SELECT * FROM %(realm)s" % {'realm': realm})
    cursor.execute("DROP TABLE %(realm)s" % {'realm': realm})

    table_metadata = TestManagerModelProvider(env).get_data_models()[realm]['table']

    env.log.info("Updating table for class %s" % realm)
    for stmt in db_backend.to_sql(table_metadata):
        env.log.debug(stmt)
        cursor.execute(stmt)

    cursor = db.cursor()

    cursor.execute("INSERT INTO %(realm)s (id,catid,page_name,name,author,time,contains_all,freeze_tc_versions) "
                   "SELECT id,catid,page_name,name,author,time,1,0 FROM %(realm)s_old" % {'realm': realm})
    cursor.execute("DROP TABLE %(realm)s_old" % {'realm': realm})
