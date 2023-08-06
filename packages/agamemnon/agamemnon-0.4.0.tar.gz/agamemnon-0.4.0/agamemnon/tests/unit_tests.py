# -*- encoding: ISO-8859-5 -*-
import random
from unittest import TestCase
from agamemnon.exceptions import NodeNotFoundException
from agamemnon.factory import load_from_file
from agamemnon.primitives import updating_node
from os import path

from nose.plugins.attrib import attr

TEST_CONFIG_FILE = path.join(path.dirname(__file__),'test_config.yml')

class AgamemnonTests(object):
    def create_node(self, node_type, id):
        attributes = {
            'boolean': True,
            'integer': id,
            'long': long(1000),
            'float': 1.5434235,
            'string': 'name%s' % id,
            'unicode': '�����'
        }
        key = 'node_%s' % id
        self.ds.create_node(node_type, key, attributes)
        node = self.ds.get_node(node_type, key)
        self.failUnlessEqual(key, node.key)
        self.failUnlessEqual(node_type, node.type)
        return key, attributes
    

    def containment(self, node_type, node):
        reference_node = self.ds.get_reference_node(node_type)
        test_reference_nodes = [rel.source_node for rel in node.instance.incoming]
        self.failUnlessEqual(1, len(test_reference_nodes))
        self.failUnlessEqual(reference_node, test_reference_nodes[0])
        ref_ref_node = self.ds.get_reference_node()
        test_reference_nodes = [rel.target_node for rel in ref_ref_node.instance.outgoing]
        self.failUnlessEqual(2, len(test_reference_nodes))
        self.failUnlessEqual(sorted([ref_ref_node, reference_node]), sorted(test_reference_nodes))
        self.failUnless(node_type in ref_ref_node.instance)
        self.failUnless(ref_ref_node.key in reference_node.instance)

    def get_set_attributes(self, node, attributes):
        self.failUnlessEqual(attributes, node.attributes)
        node['new_attribute'] = 'sample attr'
        node.commit()
        node = self.ds.get_node(node.type, node.key)
        self.failUnlessEqual('sample attr', node['new_attribute'])
        self.failIfEqual(attributes, node.attributes)
        # Test the context manager
        node = self.ds.get_node(node.type, node.key)
        with updating_node(node):
            node['new_attribute'] = 'new sample attr'
        node = self.ds.get_node(node.type, node.key)
        self.failUnlessEqual('new sample attr', node['new_attribute'])
        self.failIfEqual(attributes, node.attributes)
        with updating_node(node):
            del(node['new_attribute'])
        node = self.ds.get_node(node.type, node.key)
        if 'new_attribute' in node:
            print "We should not have found 'new_attribute' = %s" % node['new_attribute']
            self.fail()


    def create_random_relationship(self, node, target_type, node_list):
        target_key, target_attributes = random.choice(node_list)
        while target_key == node.key and not target_key in node.is_related_to:
            target_key, target_attributes = random.choice(node_list)
        attributes = {
            'int': 10,
            'float': 2.3,
            'long': long(10),
            'boolean': True,
            'string': 'string',
            'unicode': '�����'
        }
        kw_args = {
            'test_kwarg': 'kw'
        }
        target_node = self.ds.get_node(target_type, target_key)
        rel = node.is_related_to(target_node, attributes=attributes, **kw_args)
        self.failUnless(target_key in node.is_related_to)
        self.failUnless(node.key in target_node.is_related_to)
        rel_to_target = target_node.is_related_to.relationships_with(node.key)[0]
        self.failUnlessEqual(rel, rel_to_target)
        complete_attributes = {}
        complete_attributes.update(attributes)
        complete_attributes.update(kw_args)
        test_attributes = rel_to_target.attributes
        for key in complete_attributes.keys():
            self.failUnlessEqual(complete_attributes[key], test_attributes[key])
        self.failUnlessEqual(len(complete_attributes), len(test_attributes))
        self.failUnlessEqual(rel.key, rel_to_target.key)
        self.failUnless(self.ds.get_relationship(rel.type, rel.key) is not None)
        self.failUnlessEqual(len(complete_attributes), len(self.ds.get_relationship(rel.type, rel.key).attributes))
        in_outbound_relationships = False
        for rel in node.is_related_to.outgoing:
            if rel.target_node.key == target_key:
                in_outbound_relationships = True
        self.failUnless(in_outbound_relationships)
        in_inbound_relationships = False
        for rel in target_node.is_related_to.incoming:
            if rel.source_node.key == node.key:
                in_inbound_relationships = True
        self.failUnless(in_inbound_relationships)
        rel['dummy_variable'] = 'dummy'
        rel_attributes = rel.attributes
        self.failIfEqual(attributes, rel.attributes)
        self.failUnlessEqual('dummy', rel_attributes['dummy_variable'])
        del(rel['dummy_variable'])
        try:
            rel['dummy_variable']
        except KeyError:
            pass

        rel['int'] = 20
        rel.commit()
        rel_to_target = target_node.is_related_to.relationships_with(node.key)[0]
        if rel_to_target.key == rel.key:
            self.failUnlessEqual(20, rel_to_target['int'])
        return node, target_node


    def delete_relationships(self, source, target):
        source_initial_rel_count = len(source.relationships)
        target_initial_rel_count = len(target.relationships)
        self.failUnless(target.key in source.is_related_to)
        self.failUnless(source.key in target.is_related_to)
        rel_list = source.is_related_to.relationships_with(target.key)
        self.failUnlessEqual(1, len(rel_list))
        rel = rel_list[0]
        rel.delete()
        self.failIf(target.key in source.is_related_to)
        self.failIf(source.key in target.is_related_to)
        source_post_delete_count = len(source.relationships)
        target_post_delete_count = len(target.relationships)
        self.failUnlessEqual(source_initial_rel_count - 1, source_post_delete_count)
        self.failUnlessEqual(target_initial_rel_count - 1, target_post_delete_count)
        return rel

    def test_multi_get(self):
        for i in range(0, 1000):
            self.ds.create_node("test", str(i))

        nodes = self.ds.get_nodes("test", [str(i) for i in range(200, 400)])
        self.assertEqual(len(nodes), 200)


    def test_indexed_get(self):
        self.ds.create_cf("indexed")
        self.ds.create_secondary_index("indexed","color")
        self.ds.create_secondary_index("indexed","size")

        self.ds.create_node("indexed", "a", { "color": "red", "size": "small" , "num" : 1.0})
        self.ds.create_node("indexed", "b", { "color": "black", "size": "small" , "num" : 1.0 })
        self.ds.create_node("indexed", "c", { "color": "green", "size": "small" , "num" : 1.0 })
        self.ds.create_node("indexed", "e", { "color": "red", "size": "big" , "num" : 1.0 })
        self.ds.create_node("indexed", "f", { "color": "black", "size": "big" , "num" : 1.0 })
        self.ds.create_node("indexed", "g", { "color": "green", "size": "big" , "num" : 1.0 })
        

        nodes = self.ds.get_nodes_by_attr("indexed", {"color": "red"})
        self.assertEqual(len(nodes), 2)
        for node in nodes:
            self.assertTrue(node.key in ["a","e"])
            self.assertEqual(type(node["num"]), type(1.0))

        nodes = self.ds.get_nodes_by_attr("indexed", {"size": "big"})
        self.assertEqual(len(nodes), 3)
        for node in nodes:
            self.assertTrue(node.key in ["e","f","g"])
            self.assertEqual(type(node["num"]), type(1.0))

        nodes = self.ds.get_nodes_by_attr("indexed", {"size": "big", "color":"red"})
        self.assertEqual(len(nodes), 1)
        for node in nodes:
            self.assertTrue(node.key in ["e"])
            self.assertEqual(type(node["num"]), type(1.0))

    def test_update_relationship_indexes(self):
        self.ds.create_node("source", "A")
        self.ds.create_node("target", "B")
        node_a = self.ds.get_node("source", "A")
        node_b = self.ds.get_node("target", "B")

        rel = node_a.related(node_b)
        key = rel.key
        rel_key = rel.rel_key

        self.assertEqual(len(node_a.related.outgoing), 1)
        self.assertEqual(len(node_b.related.incoming), 1)

        rel["foo"] = "bar"
        rel.commit()

        # update targets so we know the denormalized 
        # indexes are being updated correctly
        node_a['fuu'] = 'fuu'
        node_a.commit()
        node_b['fee'] = 'fee'
        node_b.commit()

        self.assertEqual(len(node_a.related.outgoing), 1)
        self.assertEqual(len(node_b.related.incoming), 1)
        self.assertEqual(rel.key,  key)
        self.assertEqual(rel.rel_key,  rel_key)
        self.assertEqual(rel.source_node, node_a)
        self.assertEqual(rel.source_node.attributes, node_a.attributes)
        self.assertEqual(rel.target_node, node_b)
        self.assertEqual(rel.target_node.attributes, node_b.attributes)

        rel = node_a.related.outgoing.single


        self.assertEqual(rel['foo'], 'bar')
        rel["foo"] = "buzz"
        rel.commit()

        self.assertEqual(len(node_a.related.outgoing), 1)
        self.assertEqual(len(node_b.related.incoming), 1)
        self.assertEqual(rel.key,  key)
        self.assertEqual(rel.rel_key,  rel_key)
        self.assertEqual(rel.source_node, node_a)
        self.assertEqual(rel.source_node.attributes, node_a.attributes)
        self.assertEqual(rel.target_node, node_b)
        self.assertEqual(rel.target_node.attributes, node_b.attributes)

        node_b.related.incoming.single

        self.assertEqual(rel['foo'], 'buzz')
        rel["foo"] = "bazz"
        rel.commit()

        self.assertEqual(len(node_a.related.outgoing), 1)
        self.assertEqual(len(node_b.related.incoming), 1)
        self.assertEqual(rel.key,  key)
        self.assertEqual(rel.rel_key,  rel_key)
        self.assertEqual(rel.source_node, node_a)
        self.assertEqual(rel.source_node.attributes, node_a.attributes)
        self.assertEqual(rel.target_node, node_b)
        self.assertEqual(rel.target_node.attributes, node_b.attributes)

        rel = self.ds.get_relationship('related', key)

        self.assertEqual(rel['foo'], 'bazz')
        rel["foo"] = "bizz"
        rel.commit()

        self.assertEqual(len(node_a.related.outgoing), 1)
        self.assertEqual(len(node_b.related.incoming), 1)
        self.assertEqual(rel.key,  key)
        self.assertEqual(rel.rel_key,  rel_key)
        self.assertEqual(rel.source_node, node_a)
        self.assertEqual(rel.source_node.attributes, node_a.attributes)
        self.assertEqual(rel.target_node, node_b)
        self.assertEqual(rel.target_node.attributes, node_b.attributes)


    def test_one_node_type_one_relationship_type(self):
        """
        Tests for one node type and one relationship type.
        """
        node_type = "type_a"

        node_list = []
        for i in xrange(100):
            node_list.append(self.create_node(node_type, i))
        for key, attributes in node_list:
            node = self.ds.get_node(node_type, key)
            # test the basic details of the reference node including containment
            self.containment(node_type, node)
            # test updating the attributes of the node
            self.get_set_attributes(node, attributes)
        #Generate "random" network
        relationships = []
        for key, attributes in node_list:
            node = self.ds.get_node(node_type, key)
            for i in range(5):
                relationships.append(self.create_random_relationship(node, node_type, node_list))

        random_relationships = []
        for i in xrange(10):
            source, target = random.choice(relationships)
            self.delete_relationships(source, target)
            relationships.remove((source, target))

        for source, target in random_relationships: self.delete_relationships(source, target)

        #delete node
        deleted_nodes = []
        for i in xrange(10):
            source, target = random.choice(relationships)
            deleted_nodes.append(source)
            relationships_to_delete = [rel for rel in source.relationships]
            source.delete()
            for deleted_rel in relationships_to_delete:
                target_incoming_relationships = [rel for rel in target.is_related_to.incoming]
                self.failIf(source.key in target.is_related_to)
                self.failIf(deleted_rel in target_incoming_relationships)


    def test_large_relationship_sets(self):
        num = 1002
        node_type = "type_a"

        root = self.ds.create_node('root', 'root')
        node_list = [
            self.ds.create_node(node_type, str(i))
            for i in xrange(num)
        ]


        for node in node_list:
            node.into(root)
            root.outof(node)

        self.assertEqual(1, len(root.instance.incoming))

        self.assertEqual(num, len([rel for rel in root.outof.outgoing]))
        self.assertEqual(num, len([rel for rel in root.into.incoming]))
        self.assertEqual(num, len(root.outof.outgoing))
        self.assertEqual(num, len(root.into.incoming))

        self.assertEqual(num, len([rel for rel in root.outof]))
        self.assertEqual(num, len([rel for rel in root.into]))
        self.assertEqual(num, len(root.outof))
        self.assertEqual(num, len(root.into))

        self.assertEqual(num, len([rel for rel in root.relationships.outgoing]))
        self.assertEqual(num + 1, len([rel for rel in root.relationships.incoming]))
        self.assertEqual(num, len(root.relationships.outgoing))
        self.assertEqual(num + 1, len(root.relationships.incoming))

        self.assertEqual(2*num + 1, len([rel for rel in root.relationships]))
        self.assertEqual(2*num + 1, len(root.relationships))
@attr(backend="cassandra")
class CassandraTests(TestCase, AgamemnonTests):
    def setUp(self):
        self.ds = load_from_file(TEST_CONFIG_FILE, 'cassandra_config_1')
        self.ds.truncate()
@attr(backend="memory")
class InMemoryTests(TestCase, AgamemnonTests):
    def setUp(self):
        self.ds = load_from_file(TEST_CONFIG_FILE, 'memory_config_1')

class ElasticSearchTests(TestCase, AgamemnonTests):
    def setUp(self):
        self.ds = load_from_file(TEST_CONFIG_FILE, 'elastic_search_config')
        node_type = 'node_test'
        index_name = "test_index"
        new_index_name = "new_index"
        ns_index_name = node_type + "-_-" + index_name
        ns_new_name = node_type + "-_-" + new_index_name
        try:
            node1 = self.ds.get_node(node_type,'node_1')
            self.ds.delete_node(node1)
        except NodeNotFoundException:
            pass
        try:
            node2 = self.ds.get_node(node_type,'node_2')
            self.ds.delete_node(node2)
        except NodeNotFoundException:
            pass
        self.ds.conn.delete_index_if_exists(ns_index_name)
        self.ds.conn.delete_index_if_exists(ns_new_name)

    def index_tests(self):
        node_type = 'node_test'
        index_name = "test_index"
        new_index_name = "new_index"
        ns_index_name = node_type + "-_-" + index_name
        ns_new_name = node_type + "-_-" + new_index_name
        args = ['integer','long','float','string']
        [key1,atr1] = self.create_node(node_type,1)
        self.ds.create_index(node_type,args,index_name)
        #test to see if the index exists
        self.failUnless(ns_index_name in self.ds.conn.get_indices())
        #test to see if search function works (also populate_indices)
        node1 = self.ds.get_node(node_type,key1)
        nodes_found = self.ds.search_index(node_type,index_name,'name1')
        self.failUnless(node1 in nodes_found)
        self.failUnlessEqual(1,len(nodes_found))
        nodes_found = self.ds.search_index(node_type,index_name,'1000')
        self.failUnless(node1 in nodes_found)
        self.failUnlessEqual(1,len(nodes_found))
        #test get_indices_of_type function
        type_indices = self.ds.get_indices_of_type(node_type)
        self.failUnless(ns_index_name in type_indices)
        self.failUnlessEqual(1,len(type_indices))
        #test update_indices function
        [key2,atr2] = self.create_node(node_type,2)
        node2 = self.ds.get_node(node_type,key2)
        nodes_found = self.ds.search_index(node_type,index_name,'name2')
        self.failUnless(node2 in nodes_found)
        self.failUnlessEqual(1,len(nodes_found))
        nodes_found = self.ds.search_index(node_type,index_name,'1000')
        self.failUnless(node1 in nodes_found)
        self.failUnless(node2 in nodes_found)
        self.failUnlessEqual(2,len(nodes_found))
        #test modify_indices function
        new_args = ['string','new_attr']
        self.ds.create_index(node_type,new_args,new_index_name)
        nodes_found = self.ds.search_index(node_type,new_index_name,'new_value')
        self.failUnlessEqual(0,len(nodes_found))
        self.ds.create_node(node_type,'node_2',{'new_attr':'new_value'})
        new_node2 = self.ds.get_node(node_type,'node_2')
        nodes_found = self.ds.search_index(node_type,new_index_name,'new_value')
        self.failUnless(node1 not in nodes_found)
        self.failUnless(new_node2 in nodes_found)
        self.failUnlessEqual(1,len(nodes_found))
        #test remove_node function
        self.ds.delete_node(new_node2)
        nodes_found = self.ds.search_index(node_type,index_name,'1000')
        self.failUnlessEqual(1,len(nodes_found))
        nodes_found = self.ds.search_index(node_type,index_name,'node_2')
        self.failUnlessEqual(0,len(nodes_found))
        #test delete_index function
        num_indices = len(self.ds.conn.get_indices())
        self.ds.delete_index(node_type,index_name)
        self.ds.delete_index(node_type,new_index_name)
        self.failUnlessEqual(2,num_indices-len(self.ds.conn.get_indices()))
        self.ds.delete_node(node1)

