# -*- coding: utf-8 -*-
from dag.models import *
from dag.errors import *
from django.test import TestCase

class DifferentGraphsTestCase(TestCase):
    def test_combine_graphs(self):
        g1 = Graph.objects.create(name="graph 1")
        n1 = Node.objects.create(graph=g1)
        g2 = Graph.objects.create(name="graph 2")
        g2_id = g2.id
        n2 = Node.objects.create(graph=g2)
        self.assertRaises(SeparateGraphsError, Edge.objects.create, n1, n2)
        Edge.objects.create(n1, n2, combine_graphs=True)
        self.assertEqual(Graph.objects.all().count(), 1)
        self.assertEqual(Edge.objects.filter(graph__id=g2_id).count(), 0)
        self.assertEqual(Node.objects.filter(graph__id=g2_id).count(), 0)
    