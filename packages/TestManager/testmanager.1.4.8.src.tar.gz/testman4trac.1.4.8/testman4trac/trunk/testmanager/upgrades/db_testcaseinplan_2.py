from trac.db import Table, Column, Index, DatabaseManager

from tracgenericclass.model import create_db_for_realm
from tracgenericclass.util import *

from testmanager.model import TestManagerModelProvider

def do_upgrade(env, ver, db_backend, db):
    """
    Add 'page_version' column to testcaseinplan table
    """
    cursor = db.cursor()
    
    realm = 'testcaseinplan'
    cursor.execute("CREATE TEMPORARY TABLE %(realm)s_old AS SELECT * FROM %(realm)s" % {'realm': realm})
    cursor.execute("DROP TABLE %(realm)s" % {'realm': realm})

    table_metadata = TestManagerModelProvider(env).get_data_models()[realm]['table']

    env.log.info("Updating table for class %s" % realm)
    for stmt in db_backend.to_sql(table_metadata):
        env.log.debug(stmt)
        cursor.execute(stmt)

    cursor = db.cursor()

    cursor.execute("INSERT INTO %(realm)s (id,planid,page_name,page_version,status) "
                   "SELECT id,planid,page_name,-1,status FROM %(realm)s_old" % {'realm': realm})

    cursor.execute("DROP TABLE %(realm)s_old" % {'realm': realm})
