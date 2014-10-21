
import Boinc.configxml as configxml
from Boinc.util import *
from Boinc.db_base import *
import json

ID = '$Id$'

INIT=0
FINISHED=1

class Job(DatabaseObject):

    def getWus(self, table):
        return json.loads(self.__getattr__(self, table + "_wus"))

    def setWus(self, table, jobject):
        self.__setattr__(table + "_wus", json.dumps(jobject))

    def getErrorWus(self):
        return json.loads(self.__getattr__(self, errors))

    def setErrorWus(self, errors):
        self.__setattr__(errors, json.dumps(jobject))

    _table = DatabaseTable(
        table = 'igemhd2014',
        columns = [ 'protein',
                    'mailaddress',
                    'linker_wus',
                    'linker_state',
                    'modeller_wus',
                    'modeller_state',
                    'evaluator_wus',
                    'evaluator_state',
                    'errors',
                    ])


def connect(config = None, nodb = False):
    """Connect if not already connected, using config values."""
    if get_dbconnection():
        return 0
    config = config or configxml.default_config().config
    if nodb:
        db = ''
    else:
        db = config.db_name
    
    host=config.__dict__.get('db_host','')
    do_connect(db=db,
               host=host,
               user=config.__dict__.get('db_user',''),
               passwd=config.__dict__.get('db_passwd', ''))
    return 1

def _execute_sql_script(cursor, filename):
    for query in open(filename).read().split(';'):
        query = query.strip()
        if not query: continue
        cursor.execute(query)

connect_default_config = connect

database_classes_ = [ Job ]

Jobs = Job._table

init_table_classes(database_classes_)