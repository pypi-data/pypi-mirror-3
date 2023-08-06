import json
from pycassa import system_manager
import pycassa
from pycassa.batch import Mutator
from pycassa.cassandra.ttypes import NotFoundException, InvalidRequestException
from agamemnon.graph_constants import OUTBOUND_RELATIONSHIP_CF, INBOUND_RELATIONSHIP_CF, RELATIONSHIP_INDEX, RELATIONSHIP_CF
import pycassa.columnfamily as cf
from agamemnon.delegate import Delegate

class CassandraDataStore(Delegate):
    def __init__(self, 
                 keyspace='agamemnon', 
                 server_list=['localhost:9160'], 
                 replication_factor=1,
                 create_keyspace = False,
                **kwargs):
        super(CassandraDataStore,self).__init__()

        self._keyspace=keyspace
        self._server_list=server_list
        self._replication_factor=replication_factor
        self._pool_args = kwargs

        self._system_manager = pycassa.system_manager.SystemManager(server_list[0])
        if create_keyspace:
            self.create()

        self.init_pool()

    def init_pool(self):
        self._pool = pycassa.pool.ConnectionPool(self._keyspace,
                                                 self._server_list,
                                                 self._pool_args)

        self._cf_cache = {}
        self._index_cache = {}
        self._batch = None
        self.in_batch = False
        self.batch_count = 0
        if not self.cf_exists(OUTBOUND_RELATIONSHIP_CF):
            self.create_cf(OUTBOUND_RELATIONSHIP_CF, super=True)
        if not self.cf_exists(INBOUND_RELATIONSHIP_CF):
            self.create_cf(INBOUND_RELATIONSHIP_CF, super=True)
        if not self.cf_exists(RELATIONSHIP_INDEX):
            self.create_cf(RELATIONSHIP_INDEX, super=True)
        if not self.cf_exists(RELATIONSHIP_CF):
            self.create_cf(RELATIONSHIP_CF, super=False)


    def create(self):
        if self._keyspace not in self._system_manager.list_keyspaces():
            strategy_options = { 'replication_factor': str(self._replication_factor) } 
            self._system_manager.create_keyspace(self._keyspace, 
                                                strategy_options = strategy_options )

    def drop(self):
        self._system_manager.drop_keyspace(self._keyspace)
        self._pool.dispose()
        self._pool = None

    def truncate(self):
        try:
            self.drop()
        except InvalidRequestException:
            pass
        self.create()
        self.init_pool()

    def get_count(self, type, row, columns=None, column_start=None, super_column=None, column_finish=None):
        args = {}
        if columns is not None:
            args['columns'] = columns
        if column_start is not None:
            args['column_start'] = column_start
        if column_finish is not None:
            args['column_finish'] = column_finish
        if super_column is not None:
            args['super_column'] = super_column
        return self.get_cf(type).get_count(row, **args)

    def create_cf(self, type, column_type=system_manager.ASCII_TYPE, super=False, index_columns=list()):
        self._system_manager.create_column_family(self._keyspace, type, super=super, comparator_type=column_type)
        for column in index_columns:
            self.create_secondary_index(type, column, column_type)
        return cf.ColumnFamily(self._pool, type, autopack_names=False, autopack_values=False)

    def create_secondary_index(self, type, column, column_type=system_manager.ASCII_TYPE):
        self._system_manager.create_index(self._keyspace, type, column, column_type,
                                          index_name='%s_%s_index' % (type, column))
    
    def cf_exists(self, type):
        if type in self._cf_cache:
            return True
        try:
            cf.ColumnFamily(self._pool, type, autopack_names=False, autopack_values=False)
        except NotFoundException:
            return False
        return True

    def get_cf(self, type, create=True):

        column_family = None
        if type in self._cf_cache:
            return self._cf_cache[type]
        try:
            column_family = cf.ColumnFamily(self._pool, type, autopack_names=False, autopack_values=False)
            self._cf_cache[type] = column_family
        except NotFoundException:
            if create:
                column_family = self.create_cf(type)
        return column_family



    def insert(self, column_family, key, columns):
        if self._batch is not None:
            self._batch.insert(column_family, key, columns)
        else:
            with Mutator(self._pool) as b:
                b.insert(column_family, key, columns)

    def remove(self,column_family, key, columns=None, super_column=None):
        if self._batch is not None:
            self._batch.remove(column_family, key, columns=columns, super_column=super_column)
        else:
            column_family.remove(key, columns=columns, super_column=super_column)

    def start_batch(self, queue_size = 0):
        if self._batch is None:
            self.in_batch = True
            self._batch = Mutator(self._pool,queue_size)
        self.batch_count += 1


    def commit_batch(self):
        self.batch_count -= 1
        if not self.batch_count:
            self._batch.send()
            self._batch = None

def drop_keyspace(host_list, keyspace):
    system_manager = pycassa.SystemManager(json.loads(host_list)[0])
    system_manager.drop_keyspace(keyspace)

def create_keyspace(host_list, keyspace, **create_options):
    system_manager = pycassa.SystemManager(json.loads(host_list)[0])

    print create_options
    if "strategy_options" not in create_options:
        create_options["strategy_options"] = { 'replication_factor' : '1' }

    system_manager.create_keyspace(keyspace, **create_options)
