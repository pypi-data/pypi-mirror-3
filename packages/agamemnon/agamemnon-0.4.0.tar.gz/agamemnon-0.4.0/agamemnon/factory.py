from contextlib import contextmanager
import string
import uuid
import datetime
from dateutil.parser import parse as date_parse
from pycassa.cassandra.ttypes import NotFoundException
from pycassa.util import OrderedDict
from pycassa import index
from agamemnon.graph_constants import RELATIONSHIP_KEY_PATTERN, OUTBOUND_RELATIONSHIP_CF, RELATIONSHIP_INDEX, ENDPOINT_NAME_TEMPLATE, INBOUND_RELATIONSHIP_CF, RELATIONSHIP_CF
import pycassa
from agamemnon.cassandra import CassandraDataStore
from agamemnon.memory import InMemoryDataStore
from agamemnon.exceptions import NodeNotFoundException
import agamemnon.primitives as prim
import logging
import yaml

log = logging.getLogger(__name__)

class DataStore(object):
    def __init__(self, delegate):
        self.delegate = delegate
        for plugin in self.delegate.plugins:
            plugin_object = self.delegate.__dict__[plugin]
            plugin_object.datastore = self

    @contextmanager
    def batch(self, queue_size = 0):
        self.delegate.start_batch(queue_size = queue_size)
        yield
        self.delegate.commit_batch()

    def multiget(self, type, row_keys, **kwargs):
        column_family = self.delegate.get_cf(type)
        return [
            (key, self.deserialize_value(value))
            for key, value in column_family.multiget(row_keys, **kwargs).items()
        ]

    def get(self, type, row_key, **kwargs):
        column_family = self.delegate.get_cf(type)
        return self.deserialize_value(column_family.get(row_key, **kwargs))

    def delete(self, type, key, **kwargs):
        self.delegate.remove(self.get_cf(type), key, **kwargs)

    def insert(self, type, key, args, super_key=None):
        if not self.delegate.cf_exists(type):
            column_family = self.delegate.create_cf(type)

        else:
            column_family = self.delegate.get_cf(type)
        serialized = self.serialize_columns(args)
        if super_key is None:
            self.delegate.insert(column_family, key, serialized)
        else:
            self.delegate.insert(column_family, key, {super_key: serialized})

    def get_outgoing_relationship_count(self, source_node, relationship_type):
        column_start = '%s__' % relationship_type
        source_key = RELATIONSHIP_KEY_PATTERN % (source_node.type, source_node.key)
        try:
            return self.delegate.get_count(OUTBOUND_RELATIONSHIP_CF, source_key, column_start=column_start,
                                     column_finish='%s_`' % relationship_type)
        except NotFoundException:
            return 0

    def get_incoming_relationship_count(self, target_node, relationship_type):
        column_start = '%s__' % relationship_type
        target_key = RELATIONSHIP_KEY_PATTERN % (target_node.type, target_node.key)
        try:
            return self.delegate.get_count(INBOUND_RELATIONSHIP_CF, target_key, column_start=column_start,
                                     column_finish='%s_`' % relationship_type)
        except NotFoundException:
            return 0
    
    def get_all_outgoing_relationship_count(self,source_node):
        source_key = RELATIONSHIP_KEY_PATTERN % (source_node.type, source_node.key)
        return self.delegate.get_count(OUTBOUND_RELATIONSHIP_CF, source_key)

    def get_all_incoming_relationship_count(self, target_node):
        target_key = RELATIONSHIP_KEY_PATTERN % (target_node.type, target_node.key)
        return self.delegate.get_count(INBOUND_RELATIONSHIP_CF, target_key)

    def get_all_outgoing_relationships(self, source_node, column_count=500):
        source_key = RELATIONSHIP_KEY_PATTERN % (source_node.type, source_node.key)
        try:
            column_start = None
            while True:
                args = {'column_count': column_count}
                if column_start is not None:
                    args['column_start'] = column_start
                super_columns = self.get(OUTBOUND_RELATIONSHIP_CF, source_key, **args)
                for super_column in super_columns.items():
                    if super_column[0] == column_start: continue
                    yield self.get_outgoing_relationship(super_column[1]['rel_type'], source_node, super_column)
                if len(super_columns) < column_count:
                    return
                column_start = super_columns.items()[-1][0]
        except NotFoundException:
            return

    def get_all_incoming_relationships(self, target_node, column_count=500):
        target_key = RELATIONSHIP_KEY_PATTERN % (target_node.type, target_node.key)
        try:
            column_start = None
            while True:
                args = {'column_count': column_count}
                if column_start is not None:
                    args['column_start'] = column_start
                super_columns = self.get(INBOUND_RELATIONSHIP_CF, target_key, **args)
                for super_column in super_columns.items():
                    if super_column[0] == column_start: continue
                    yield self.get_incoming_relationship(super_column[1]['rel_type'], target_node, super_column)
                if len(super_columns) < column_count:
                    return
                column_start = super_columns.items()[-1][0]
        except NotFoundException:
            return
        
    def get_outgoing_relationships(self, source_node, rel_type, count=500):
        source_key = RELATIONSHIP_KEY_PATTERN % (source_node.type, source_node.key)
        #Ok, this is weird.  So in order to get a column slice, you need to provide a start that is <= your first column
        #id, and a finish which is >= your last column.  Since our columns are sorted by ascii, this means we need to go
        #from rel_type_ to rel_type` because "`" is the char 1 greater than "_", so this will get anything which starts
        #rel_type_.  Now I realize that this could problems when there is a "_" in the relationship name, so we will
        #probably need a different delimiter.
        #TODO: fix delimiter
        try:
            column_start = '%s__' % rel_type
            while True:
                super_columns = self.get(OUTBOUND_RELATIONSHIP_CF, source_key, column_start=column_start,
                                     column_finish='%s_`' % rel_type, column_count=count)
                for super_column in super_columns.items():
                    if super_column[0] == column_start: continue
                    yield self.get_outgoing_relationship(rel_type, source_node, super_column)
                if len(super_columns) < count:
                    return
                column_start = super_columns.items()[-1][0]
        except NotFoundException:
            return


    def get_incoming_relationships(self, target_node, rel_type, count=500):
        target_key = RELATIONSHIP_KEY_PATTERN % (target_node.type, target_node.key)
        #Ok, this is weird.  So in order to get a column slice, you need to provide a start that is <= your first column
        #id, and a finish which is >= your last column.  Since our columns are sorted by ascii, this means we need to go
        #from rel_type_ to rel_type` because "`" is the char 1 greater than "_", so this will get anything which starts
        #rel_type_.  Now I realize that this could problems when there is a "_" in the relationship name, so we will
        #probably need a different delimiter.
        #TODO: fix delimiter
        try:
            column_start = '%s__' % rel_type
            while True:
                super_columns = self.get(INBOUND_RELATIONSHIP_CF, target_key, column_start=column_start,
                                     column_finish='%s_`' % rel_type, column_count=count)
                for super_column in super_columns.items():
                    if super_column[0] == column_start: continue
                    yield self.get_incoming_relationship(rel_type, target_node, super_column)
                if len(super_columns) < count:
                    return
                column_start = super_columns.items()[-1][0]
        except NotFoundException:
            return


    def get_outgoing_relationship(self, rel_type, source_node, super_column):
        """
        Process the contents of a SuperColumn to extract the relationship and to_node properties and return
        a constructed relationship
        """
        rel_key = super_column[0]
        target_node_key = None
        target_node_type = None
        target_attributes = {}
        rel_attributes = {}
        for column in super_column[1].keys():
            value = super_column[1][column]
            if column == 'target__type':
                target_node_type = value
            elif column == 'target__key':
                target_node_key = value
            elif column.startswith('target__'):
                target_attributes[column[8:]] = value
            else:
                rel_attributes[column] = value
        return prim.Relationship(rel_key, source_node,
                                 prim.Node(self, target_node_type, target_node_key, target_attributes), self
                                 , rel_type,
                                 rel_attributes)

    def get_incoming_relationship(self, rel_type, target_node, super_column):
        """
        Process the contents of a SuperColumn to extract an incoming relationship and the associated from_node and
        return a constructed relationship
        """
        rel_key = super_column[0]
        source_node_key = None
        source_node_type = None
        source_attributes = {}
        rel_attributes = {}
        for column in super_column[1].keys():
            value = super_column[1][column]
            if column == 'source__type':
                source_node_type = value
            elif column == 'source__key':
                source_node_key = value
            elif column.startswith('source__'):
                source_attributes[column[8:]] = value
            else:
                rel_attributes[column] = value
        return prim.Relationship(rel_key, prim.Node(self, source_node_type, source_node_key, source_attributes),
                                 target_node,
                                 self, rel_type, rel_attributes)


    def delete_relationship(self, rel_type, rel_key, rel_id, from_type, from_key, to_type, to_key):
        rel_from_key = ENDPOINT_NAME_TEMPLATE % (from_type, from_key)
        rel_to_key = ENDPOINT_NAME_TEMPLATE % (to_type, to_key)

        with self.batch():
            self.delete(INBOUND_RELATIONSHIP_CF, rel_to_key, super_column=rel_id)
            self.delete(OUTBOUND_RELATIONSHIP_CF, rel_from_key, super_column=rel_id)
            self.delete(RELATIONSHIP_INDEX, rel_to_key, super_column=from_key, columns=[rel_type])
            self.delete(RELATIONSHIP_INDEX, rel_from_key, super_column=to_key, columns=[rel_type])
            self.delete(RELATIONSHIP_CF, ENDPOINT_NAME_TEMPLATE % (rel_type, rel_key))

    def create_relationship(self, rel_type, source_node, target_node, key=None, args=dict()):
        if key is None:
            key = str(uuid.uuid4())
            #node relationship types
        rel_key = RELATIONSHIP_KEY_PATTERN % (rel_type, key)
        with self.batch():
            #outbound_cf
            columns = {'rel_type': rel_type, 'rel_key': key}
            #add relationship attributes
            columns.update(args)
            rel_attr = dict(columns)
            #add target attributes
            columns['target__type'] = target_node.type.encode('ascii')
            columns['target__key'] = target_node.key.encode('ascii')
            target_attributes = target_node.attributes
            for attribute_key in target_attributes.keys():
                columns['target__%s' % attribute_key] = target_attributes[attribute_key]
            columns['source__type'] = source_node.type.encode('ascii')
            columns['source__key'] = source_node.key.encode('ascii')
            source_attributes = source_node.attributes
            for attribute_key in source_attributes.keys():
                columns['source__%s' % attribute_key] = source_attributes[attribute_key]

            source_key = ENDPOINT_NAME_TEMPLATE % (source_node.type, source_node.key)
            target_key = ENDPOINT_NAME_TEMPLATE % (target_node.type, target_node.key)
            serialized = self.serialize_columns(columns)
            self.insert(RELATIONSHIP_CF, ENDPOINT_NAME_TEMPLATE % (rel_type, key), serialized)
            self.insert(OUTBOUND_RELATIONSHIP_CF, source_key, {rel_key: serialized})
            self.insert(INBOUND_RELATIONSHIP_CF, target_key, {rel_key: serialized})

            #            relationship_index_cf = self.delegate.get_cf(RELATIONSHIP_INDEX)
            # Add entries in the relationship index
            self.insert(RELATIONSHIP_INDEX, source_key, {target_node.key: {rel_type: '%s__outgoing' % rel_key}})
            self.insert(RELATIONSHIP_INDEX, target_key, {source_node.key: {rel_type: '%s__incoming' % rel_key}})

        #created relationship object
        return prim.Relationship(rel_key, source_node, target_node, self, rel_type, rel_attr)

    def get_relationship(self, rel_type, rel_key):
        try:
            values = self.get(RELATIONSHIP_CF, ENDPOINT_NAME_TEMPLATE % (rel_type, rel_key)) 
        except NotFoundException:
            raise NodeNotFoundException()
        source_node_key = None
        source_node_type = None
        source_attributes = {}
        for column in values.keys():
            value = values[column]
            if column == 'source__type':
                source_node_type = value
            elif column == 'source__key':
                source_node_key = value
            elif column.startswith('source__'):
                source_attributes[column[8:]] = value
        source = prim.Node(self, source_node_type, source_node_key, source_attributes)
        rel_key = RELATIONSHIP_KEY_PATTERN % (rel_type, rel_key)
        return self.get_outgoing_relationship(rel_type, source, (rel_key, values))

    def has_relationship(self, node_a, node_b_key, rel_type):
        """
        This determines if two nodes have a relationship of the specified type.

        > ds = DataStore()
        > node_a =

        """
        node_a_row_key = ENDPOINT_NAME_TEMPLATE % (node_a.type, node_a.key)
        rel_list = []
        try:
            rels = self.get(RELATIONSHIP_INDEX, node_a_row_key, super_column=node_b_key, columns=[rel_type])
            for rel in rels.values():
                if rel.endswith('__incoming'):
                    rel_id = string.replace(rel, '__incoming', '')
                    super_column = self.get(INBOUND_RELATIONSHIP_CF, node_a_row_key, columns=[rel_id]).items()[0]
                    relationship = self.get_incoming_relationship(rel_type, node_a, super_column)
                elif rel.endswith('__outgoing'):
                    rel_id = string.replace(rel, '__outgoing', '')
                    super_column = self.get(OUTBOUND_RELATIONSHIP_CF, node_a_row_key, columns=[rel_id]).items()[0]
                    relationship = self.get_outgoing_relationship(rel_type, node_a, super_column)
                else:
                    continue

                rel_list.append(relationship)
        except NotFoundException:
            pass
        return rel_list

    def create_node(self, type, key, args=None, reference=False):
        if args is None:
            args = {}
        try:
            node = self.get_node(type, key)
            node.attributes.update(args)
            self.save_node(node)
            self.delegate.on_modify(node)
            return node
        except NodeNotFoundException:
            #since node won't get created without args, we will include __id by default
            args["__id"] = key
            serialized = self.serialize_columns(args)
            self.insert(type, key, serialized)
            node = prim.Node(self, type, key, args)
            if not reference:
                #this adds the created node to the reference node for this type of object
                #that reference node functions as an index to easily access all nodes of a specific type
                reference_node = self.get_reference_node(type)
                reference_node.instance(node, key=key)
            self.delegate.on_create(node)
            return node

    def delete_node(self, node):
        relationships = node.relationships
        self.delegate.on_delete(node)
        with self.batch():
           for rel in relationships:
                rel.delete()
                self.delete(node.type, node.key)

    def save_node(self, node):
        """
        This needs to update the entry in the type table as well as all of the relationships
        """
        with self.batch():
            log.debug("Saving node: {0}: {1}".format(node.type, node.key))
            self.insert(node.type, node.key, self.serialize_columns(node.attributes))
            columns_to_remove = []
            for key in node.old_values:
                if not key in node.new_values:
                    columns_to_remove.append(key)
            if len(columns_to_remove) > 0:
                self.remove(self.get_cf(node.type), node.key, columns=columns_to_remove)
            source_key = ENDPOINT_NAME_TEMPLATE % (node.type, node.key)
            target_key = ENDPOINT_NAME_TEMPLATE % (node.type, node.key)

            try:
                next_start_id = ""
                num_columns = self.delegate.get_count(OUTBOUND_RELATIONSHIP_CF, source_key, column_start=next_start_id)
                outbound_results = self.get(OUTBOUND_RELATIONSHIP_CF, source_key,
                                            column_start=next_start_id, column_count=num_columns)
            except NotFoundException:
                log.debug("No outgoing relationships for {0}: {1}".format(node.type, node.key))
                outbound_results = {}
            try:
                next_start_id = ""
                inbound_results = {}
                num_columns = self.delegate.get_count(INBOUND_RELATIONSHIP_CF, target_key, column_start=next_start_id)
                inbound_results = self.get(INBOUND_RELATIONSHIP_CF, target_key,
                                        column_start=next_start_id, column_count=num_columns)
            except NotFoundException:
                log.debug("No incoming relationships for {0}: {1}".format(node.type, node.key))
                inbound_results = {}

            outbound_columns = {'source__type': node.type.encode('utf-8'), 'source__key': node.key.encode('utf-8')}
            node_attributes = node.attributes
            for attribute_key in node.attributes.keys():
                outbound_columns['source__%s' % attribute_key] = node_attributes[attribute_key]
            for key in outbound_results.keys():
                target = outbound_results[key]
                target_key = ENDPOINT_NAME_TEMPLATE % (target['target__type'], target['target__key'])
                target.update(outbound_columns)
                serialized = self.serialize_columns(target)
                self.insert(OUTBOUND_RELATIONSHIP_CF, source_key, serialized, key)
                self.insert(INBOUND_RELATIONSHIP_CF, target_key, serialized, key)
                self.insert(RELATIONSHIP_CF, key, serialized)
                if len(columns_to_remove):
                    self.delete(OUTBOUND_RELATIONSHIP_CF, source_key, super_column=key,
                            columns=['source__%s' % column for column in columns_to_remove])
                    self.delete(INBOUND_RELATIONSHIP_CF, target_key, super_column=key,
                            columns=['source__%s' % column for column in columns_to_remove])
                    self.remove(self.get_cf(RELATIONSHIP_CF), key,
                            columns=['source__%s' % column for column in columns_to_remove])
            inbound_columns = {'target__type': node.type.encode('utf-8'), 'target__key': node.key.encode('utf-8')}
            for attribute_key in node.attributes.keys():
                inbound_columns['target__%s' % attribute_key] = node_attributes[attribute_key]
            for key in inbound_results.keys():
                source = inbound_results[key]
                source_key = ENDPOINT_NAME_TEMPLATE % (source['source__type'], source['source__key'])
                target_key = ENDPOINT_NAME_TEMPLATE % (node.type, node.key)
                source.update(inbound_columns)
                serialized = self.serialize_columns(source)
                self.insert(OUTBOUND_RELATIONSHIP_CF, source_key, serialized, key)
                self.insert(INBOUND_RELATIONSHIP_CF, target_key, serialized, key)
                self.insert(RELATIONSHIP_CF, key, serialized)
                if len(columns_to_remove):
                    self.delete(OUTBOUND_RELATIONSHIP_CF, source_key, super_column=key,
                            columns=['target__%s' % column for column in columns_to_remove])
                    self.delete(INBOUND_RELATIONSHIP_CF, target_key, super_column=key,
                            columns=['target__%s' % column for column in columns_to_remove])
                    self.remove(self.get_cf(RELATIONSHIP_CF), key,
                            columns=['target__%s' % column for column in columns_to_remove])

    def get_node(self, type, key):
        try:
            values = self.get(type, key)
        except NotFoundException:
            raise NodeNotFoundException()
        return prim.Node(self, type, key, values)

    def get_nodes(self, type, keys):
        try:
            rows = self.multiget(type, keys)
        except NotFoundException:
            raise NodeNotFoundException()
        return [ 
            prim.Node(self, type, key, values)
            for key, values in rows
        ]

    def get_nodes_by_attr(self, type, attrs = {}, expressions=None, start_key='', row_count = 2147483647, **kwargs):
        if expressions is None:
            expressions = []
        for attr, value in self.serialize_columns(attrs).items():
            expressions.append(index.create_index_expression(attr, value))

        clause = index.create_index_clause(expressions, start_key=start_key, count=row_count)
        try:
            column_family = self.delegate.get_cf(type)
            rows = column_family.get_indexed_slices(clause, **kwargs)
        except NotFoundException:
            raise NodeNotFoundException()
        return [
            prim.Node(self, type, key, self.deserialize_value(values))
            for key, values in rows
        ]

        

    def get_reference_node(self, name='reference'):
        """
        Nodes returned here are very easily referenced by name and then function as an index for all attached nodes
        The most typical use case is to index all of the nodes of a certain type, but the functionality is not limited
        to this.
        """
        try:
            ref_node = self.get_node('reference', name)
        except NodeNotFoundException:
            ref_node = self.create_node('reference', name, {'reference': 'reference'}, reference=True)
            self.get_reference_node().instance(ref_node, key='reference_%s' % name)

        return ref_node

    def deserialize_value(self, value):
        if isinstance(value, dict):
            return self.deserialize_columns(value)
        if not value.startswith('$'):
            return value
        type = value[:2]
        content = value[2:]
        if type == '$b':
            if content == 'True':
                return True
            if content == 'False':
                return False
        elif type == '$i':
            return int(content)
        elif type == '$l':
            return long(content)
        elif type == '$f':
            return float(content)
        elif type == '$t':
            return date_parse(content)

    def serialize_value(self, value):
        if type(value) == bool:
            return '$b%r' % value
        elif type(value) == int:
            return '$i%r' % value
        elif type(value) == long:
            return '$l%r' % value
        elif type(value) == float:
            return '$f%r' % value
        elif isinstance(value, unicode):
            return value.encode('utf-8')
        elif isinstance(value, dict):
            return self.serialize_columns(value)
        elif isinstance(value, datetime.datetime):
            return '$t%s' % value.isoformat()
        else:
            return value

    def deserialize_columns(self, columns):
        return OrderedDict([(key, self.deserialize_value(value))
        for key, value in columns.items()
        if value is not None])

    def serialize_columns(self, columns):
        return OrderedDict([(key, self.serialize_value(value))
        for key, value in columns.items()
        if value is not None])

    def __getattr__(self, item):
        if not item in self.__dict__:
            return getattr(self.delegate, item)

def load_from_file(config_file, key=None):
    """
    Load the specified yaml file. If :key is set, then we will use that as the
    top level attribute of the yaml file that holds the config, otherwise, we
    assume the whole yaml file is the config.
    """
    with open(config_file) as f:
        settings = yaml.load(f)
    if key is not None:
        settings = settings[key]

    return load_from_settings(settings)


def load_from_settings(settings):
    settings['plugins'] = settings.get('plugins',{})
    settings['backend_config'] = settings.get('backend_config',{})

    # load delegate
    module_name, cls_name = settings['backend'].rsplit('.',1)
    module = __import__(module_name, fromlist=[cls_name])
    cls = getattr(module, cls_name)
    delegate = cls(**settings['backend_config'])
    delegate.load_plugins(settings['plugins'])
    return DataStore(delegate)
