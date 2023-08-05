# -*- coding: utf-8 -*-
from dag.models import *
from dag.errors import *
from models import *
from django.test import TestCase

class ContentTypeTestCase(TestCase):

    def test_basic(self):
        """
Test basic tree layout.

          Chur
         /    \
      Zurich  Bern
     /    \  /     \
  Geneva  Lucern  Lausanne
    |       |
Winterthur  |
       \    |
       Glarus
        """
        g = Graph.objects.create(name="graph")
        zurich = City.objects.create(name="Zurich")
        bern = City.objects.create(name="Bern")
        geneva = City.objects.create(name="Geneva")
        lucern = City.objects.create(name="Luzern")
        lausanne = City.objects.create(name="Lausanne")
        winterthur = City.objects.create(name="Winterthur")
        glarus = City.objects.create(name="Glarus")
        chur = City.objects.create(name="Chur")
        zurich_node = Node(graph=g)
        zurich_node.reference = zurich
        zurich_node.save()
        geneva_node = Node(graph=g)
        geneva_node.reference = geneva
        geneva_node.save()
        bern_node = Node(graph=g)
        bern_node.reference = bern
        bern_node.save()
        lucern_node = Node(graph=g)
        lucern_node.reference = lucern
        lucern_node.save()
        lausanne_node = Node(graph=g)
        lausanne_node.reference = lausanne
        lausanne_node.save()
        winterthur_node = Node(graph=g)
        winterthur_node.reference = winterthur
        winterthur_node.save()
        glarus_node = Node(graph=g)
        glarus_node.reference = glarus
        glarus_node.save()
        chur_node = Node(graph=g)
        chur_node.reference = chur
        chur_node.save()
        Edge.objects.create(zurich_node, chur_node)
        Edge.objects.create(bern_node, chur_node)
        Edge.objects.create(glarus_node, winterthur_node)
        Edge.objects.create(glarus_node, lucern_node)
        Edge.objects.create(lucern_node, bern_node)
        Edge.objects.create(geneva_node, zurich_node)
        Edge.objects.create(lausanne_node, bern_node)
        Edge.objects.create(winterthur_node, geneva_node)
        Edge.objects.create(lucern_node, zurich_node)
        self.assertEqual(lucern.get_parents(), [zurich, bern])
        self.assertEqual(lucern.get_children(), [glarus,])
        self.assertEqual(lucern.get_descendants(), [glarus,])
        self.assertEqual(lucern.get_ancestors(), [zurich, bern, chur])
        self.assertEqual(glarus.get_descendants(), [])
        self.assertEqual(glarus.get_children(), [])
        self.assertEqual(glarus.get_parents(), [lucern, winterthur])
        self.assertEqual(glarus.get_ancestors(), [lucern, winterthur, zurich, 
            bern, geneva, chur])
        self.assertEqual(chur.get_ancestors(), [])
        self.assertEqual(chur.get_descendants(), [zurich, bern, geneva, 
            lucern, lausanne, winterthur, glarus])
        e = Edge.objects.get(graph=g, node_from=lucern, node_to=zurich)
        e.delete()
        self.assertEqual(zurich.get_children(), [geneva,])
        self.assertEqual(zurich.get_descendants(), [geneva, winterthur, 
            glarus])
        self.assertFalse(g.is_heterogeneous)
    
    def test_multiple_ct_references(self):
        g = Graph.objects.create(name="graph")
        zurich = City.objects.create(name="Zurich")
        n1 = Node(graph=g)
        n1.reference = zurich
        n1.save()
        n2 = Node(graph=g)
        n2.reference = zurich
        self.assertRaises(MultipleReferencesError, n2.save)
    
    def test_heterogeneous_trees_1(self):
        """Test heterogeneous trees with manual node references"""
        g = Graph.objects.create(name="graph")
        zurich = City.objects.create(name="Zurich")
        zurich_node = Node(graph=g)
        zurich_node.reference = zurich
        zurich_node.save()
        bern = City.objects.create(name="Bern")
        bern_node = Node(graph=g)
        bern_node.reference = bern
        bern_node.save()
        blue = Color.objects.create(name="Blue")
        blue_node = Node(graph=g)
        blue_node.reference = blue
        blue_node.save()
        green = Color.objects.create(name="Green")
        green_node = Node(graph=g)
        green_node.reference = green
        green_node.save()
        Edge.objects.create(blue_node, zurich_node)
        Edge.objects.create(bern_node, blue_node)
        Edge.objects.create(green_node, bern_node)
        self.assertEqual(zurich.get_descendants(), [blue, bern, green])
        self.assertTrue(g.is_heterogeneous)
    
    def test_heterogeneous_trees_2(self):
        """Test heterogeneous trees with automatic node references"""
        g = Graph.objects.create(name="graph")
        zurich = City.objects.create(name="Zurich")
        bern = City.objects.create(name="Bern")
        blue = Color.objects.create(name="Blue")
        green = Color.objects.create(name="Green")
        Edge.objects.create(node_from=zurich.node(g), node_to=blue.node(g), 
            graph=g)
        Edge.objects.create(node_from=blue.node(g), node_to=bern.node(g), 
            graph=g)
        Edge.objects.create(bern.node(g), green.node(g), graph=g)
        self.assertEqual(zurich.get_ancestors(graph=g), [blue, bern, green])
        self.assertTrue(g.is_heterogeneous)
    
    def test_blank_nodes(self):
        g = Graph.objects.create(name="graph")
        zurich = City.objects.create(name="Zurich")
        bern = City.objects.create(name="Bern")
        blank_node = Node.objects.create(graph=g)
        Edge.objects.create(node_from=zurich.node(g), node_to=blank_node, 
            graph=g)
        Edge.objects.create(node_from=blank_node, node_to=bern.node(g), 
            graph=g)
        self.assertEqual(zurich.get_ancestors(), [blank_node, bern])
    
    def test_edge_creation_without_node_creation(self):
        g = Graph.objects.create(name="graph")
        zurich = City.objects.create(name="Zurich")
        bern = City.objects.create(name="Bern")
        geneva = City.objects.create(name="Geneva")
        Edge.objects.create(node_from=zurich.node(g), node_to=bern.node(g), 
            graph=g)
        Edge.objects.create(node_from=bern.node(g), node_to=geneva.node(g), 
            graph=g)
        self.assertEqual(zurich.get_ancestors(), [bern, geneva])
    
    def test_counts(self):
        """
Test counts for ancestor, descendants, etc.

          Chur
         /    \
      Zurich  Bern
     /    \  /
  Geneva  Lucern
        """
        g = Graph.objects.create(name="graph")
        zurich = City.objects.create(name="Zurich")
        bern = City.objects.create(name="Bern")
        geneva = City.objects.create(name="Geneva")
        lucern = City.objects.create(name="Luzern")
        lausanne = City.objects.create(name="Lausanne")
        winterthur = City.objects.create(name="Winterthur")
        glarus = City.objects.create(name="Glarus")
        chur = City.objects.create(name="Chur")
        zurich_node = Node(graph=g)
        zurich_node.reference = zurich
        zurich_node.save()
        geneva_node = Node(graph=g)
        geneva_node.reference = geneva
        geneva_node.save()
        bern_node = Node(graph=g)
        bern_node.reference = bern
        bern_node.save()
        lucern_node = Node(graph=g)
        lucern_node.reference = lucern
        lucern_node.save()
        chur_node = Node(graph=g)
        chur_node.reference = chur
        chur_node.save()
        Edge.objects.create(zurich_node, chur_node)
        Edge.objects.create(bern_node, chur_node)
        Edge.objects.create(lucern_node, bern_node)
        Edge.objects.create(geneva_node, zurich_node)
        Edge.objects.create(lucern_node, zurich_node)
        
        self.assertEqual(chur.get_child_count(), 2)
        self.assertFalse(chur.is_child_node())
        self.assertFalse(chur.is_leaf_node())
        self.assertTrue(chur.is_root_node())
        self.assertEqual(chur.get_descendant_count(), 4)
        self.assertEqual(chur.get_parent_count(), 0)
        self.assertEqual(chur.get_ancestor_count(), 0)
        
        self.assertEqual(zurich.get_child_count(), 2)
        self.assertTrue(zurich.is_child_node())
        self.assertFalse(zurich.is_leaf_node())
        self.assertFalse(zurich.is_root_node())
        self.assertEqual(zurich.get_descendant_count(), 2)
        self.assertEqual(zurich.get_parent_count(), 1)
        self.assertEqual(zurich.get_ancestor_count(), 1)
        
        self.assertEqual(lucern.get_child_count(), 0)
        self.assertTrue(lucern.is_child_node())
        self.assertTrue(lucern.is_leaf_node())
        self.assertFalse(lucern.is_root_node())
        self.assertEqual(lucern.get_descendant_count(), 0)
        self.assertEqual(lucern.get_parent_count(), 2)
        self.assertEqual(lucern.get_ancestor_count(), 3)
    
    def test_root_nodes(self):
        """
     Zurich  Bern
     /    \  /
    Geneva  Lucern
        """
        g = Graph.objects.create(name="graph")
        zurich = City.objects.create(name="Zurich")
        bern = City.objects.create(name="Bern")
        geneva = City.objects.create(name="Geneva")
        lucern = City.objects.create(name="Luzern")
        zurich_node = Node(graph=g)
        zurich_node.reference = zurich
        zurich_node.save()
        geneva_node = Node(graph=g)
        geneva_node.reference = geneva
        geneva_node.save()
        bern_node = Node(graph=g)
        bern_node.reference = bern
        bern_node.save()
        lucern_node = Node(graph=g)
        lucern_node.reference = lucern
        lucern_node.save()
        Edge.objects.create(bern_node, lucern_node)
        Edge.objects.create(zurich_node, geneva_node)
        Edge.objects.create(zurich_node, lucern_node)
        self.assertEqual(set(g.root_nodes), set([bern_node, zurich_node]))
        self.assertEqual(set(g.root_node_objects), set([zurich, bern]))
        