# -*- coding: utf-8 -*-
from dag.models import *
from dag.errors import *
from django.test import TestCase

class DatabaseTestCase(TestCase):

    def test_basic(self):
        g = Graph.objects.create(name="graph")
        n1 = Node.objects.create(graph=g)
        n2 = Node.objects.create(graph=g)
        n3 = Node.objects.create(graph=g)
        Edge.objects.create(n1, n2)
        Edge.objects.create(n2, n3)
        self.assertEqual(Node.objects.all().count(), 3)
        self.assertEqual(Edge.objects.all().count(), 2)
        self.assertEqual(TransitiveClosure.objects.all().count(), 3)
    
    def test_linking_same_node(self):
        g = Graph.objects.create(name="graph")
        n1 = Node.objects.create(graph=g)
        self.assertRaises(CircularReferenceError, Edge.objects.create, n1, n1)
        self.assertRaises(CircularReferenceError, Edge.objects.create, n1, n1, 
            g)
    
    def test_circular_reference(self):
        g = Graph.objects.create(name="graph")
        n1 = Node.objects.create(graph=g)
        n2 = Node.objects.create(graph=g)
        n3 = Node.objects.create(graph=g)
        Edge.objects.create(n1, n2)
        Edge.objects.create(n2, n3)
        self.assertRaises(CircularReferenceError, Edge.objects.create, n3, n1)
    
    def test_delete_edge(self):
        g = Graph.objects.create(name="graph")
        n1 = Node.objects.create(graph=g)
        n2 = Node.objects.create(graph=g)
        n3 = Node.objects.create(graph=g)
        Edge.objects.create(n1, n2)
        Edge.objects.create(n2, n3)
        Edge.objects.get(node_from=n1, node_to=n2).delete()
        self.assertEqual(Node.objects.all().count(), 3)
        self.assertEqual(Edge.objects.all().count(), 1)
        self.assertEqual(TransitiveClosure.objects.all().count(), 1)
    
    def test_update_edge(self):
        g = Graph.objects.create(name="graph")
        n1 = Node.objects.create(graph=g)
        n2 = Node.objects.create(graph=g)
        n3 = Node.objects.create(graph=g)
        Edge.objects.create(n1, n2)
        e = Edge.objects.get(node_from=n1, node_to=n2)
        e.node_to = n3
        self.assertRaises(NotImplementedError, e.save)
    
    def test_add_duplicate_edge(self):
        g = Graph.objects.create(name="graph")
        n1 = Node.objects.create(graph=g)
        n2 = Node.objects.create(graph=g)
        n3 = Node.objects.create(graph=g)
        Edge.objects.create(n1, n2)
        self.assertRaises(DuplicateEdgeError, Edge.objects.create, n1, n2)
    
    def test_diamond(self):
        g = Graph.objects.create(name="graph")
        n1 = Node.objects.create(graph=g)
        n2 = Node.objects.create(graph=g)
        n3 = Node.objects.create(graph=g)
        n4 = Node.objects.create(graph=g)
        Edge.objects.create(n1, n2)
        Edge.objects.create(n1, n3)
        Edge.objects.create(n2, n4)
        Edge.objects.create(n3, n4)
        self.assertEqual(TransitiveClosure.objects.filter(depth=1).count(), 2)
        self.assertEqual(TransitiveClosure.objects.filter(node_from=n1, 
            node_to=n4).count(), 2)
        self.assertEqual(TransitiveClosure.objects.all().count(), 6)
        Edge.objects.get(node_from=n3, node_to=n4).delete()
        self.assertEqual(TransitiveClosure.objects.filter(depth=1).count(), 1)
        self.assertEqual(TransitiveClosure.objects.filter(node_from=n1, 
            node_to=n4).count(), 1)
        self.assertEqual(TransitiveClosure.objects.all().count(), 4)
