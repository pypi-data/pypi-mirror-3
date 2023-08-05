from django.db import models
from django.utils.translation import ugettext as _
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from errors import *
from utils import create_objects_iterable, flatten

class Graph(models.Model):
    name = models.TextField(unique=True)
    
    class Meta:
        db_table = "dag_graph"
    
    def __unicode__(self):
        return "Graph: %s" % self.name
    
    @property
    def is_heterogeneous(self):
        return self.content_types_number > 1
    
    @property
    def content_types_number(self):
        return Node.objects.filter(graph=self).values('content_type'
            ).distinct().count()

    def combine_graphs(self, other, delete=True):
        if not isinstance(other, Graph):
            raise TypeError, "Must combine with Graph instance."
        
        # Check for multiple references
        first_nodes = Node.objects.filter(graph__id=self.id).values_list("id", 
            flat=True)
        second_nodes = Node.objects.filter(graph__id=other.id).values_list( 
            "id", flat=True)
        if list(set(first_nodes).intersection(set(second_nodes))):
            raise MultipleReferencesError, \
                "Can't combine graphs with the same node"
        
        edges = Edge.objects.filter(graph=other).values("node_from", 
            "node_to")
        nodes = Node.objects.filter(graph=other)
        nodes.update(graph=self)
        
        # Will delete TransitiveClosure objects on cascade
        Edge.objects.filter(graph=other).delete()
        
        # Cache in dictionary for speedy lookups
        node_dict = {}
        for d in edges:
            if d["node_from"] not in node_dict:
                d["node_from"] = Node.objects.get(id=d["node_from"])
            if d["node_to"] not in node_dict:
                d["node_to"] = Node.objects.get(id=d["node_to"])
            Edge.objects.create(d["node_from"], d["node_to"], graph=self)
        
        if delete:
            other.delete()
    
    @property
    def root_nodes(self):
        """Get root nodes for a graph"""
        return Node.objects.filter(graph=self).exclude(
            id__in=Edge.objects.filter(node_to__graph=self).values_list(
            'node_to', flat=True))

    @property
    def root_node_objects(self):
        """Get objects for root nodes helper"""
        root_nodes = self.root_nodes
    
        tc_query = root_nodes.values_list('graph', 'id', 'content_type', 
            'object_id')
    
        # Create dictionary with content type ids as keys, and objects ids 
        # as values
        content_type_dict = {}
        for tup in tc_query:
            content_type_dict.setdefault(tup[2], []).append(tup[3])

        # Get queryset per content type, and aggregate together
        content_types = ContentType.objects.filter(
            id__in=content_type_dict.keys())
        objs = flatten([create_objects_iterable(c, content_type_dict
            ) for c in content_types])
        return objs


class Node(models.Model):
    graph = models.ForeignKey(Graph)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    reference = generic.GenericForeignKey('content_type', 'object_id')
    
    class Meta:
        db_table = "dag_node"
        unique_together = ("graph", "content_type", "object_id")
    
    def save(self, *args, **kwargs):
        # Check for content_type / graph uniqueness upon obj creation
        if not self.id and self.content_type and self.object_id:
            if Node.objects.filter(content_type=self.content_type, 
                    object_id=self.object_id, graph=self.graph).count():
                raise MultipleReferencesError, "An existing node already " + \
                    "exists for this object reference and graph"
        super(Node, self).save(*args, **kwargs)
    
    def __unicode__(self):
        if self.object_id:
            return "Node: %s" % self.reference
        else:
            return "<Node object with id %s at address %s>" % (self.id, 
                id(self))
    
    def link_to(self, other_node):
        return Edge.objects.create(self, other_node, graph=self.graph)
    
    def link_from(self, other_node):
        return Edge.objects.create(other_node, self, graph=self.graph)


class EdgeManager(models.Manager):
    def update(self):
        raise NotImplementedError, \
            "Edges can't be updated - they must be deleted and re-created."
    
    def _parse_to_node(self, node, graph):
        # Make sure objects exist in database
        try:
            # Is this the best way to test if an object has been saved?
            assert node.pk
        except AssertionError:
            raise AttributeError, \
                "Can only link nodes already saved in database"
        
        if isinstance(node, Node):
            return node
        try:
            _node = node.node()
            if _node:
                return _node
            else:
                if not graph:
                    raise MissingGraphError, \
                        "Must specify graph when creating new node."
                return Node.objects.create(graph=graph, object_id=node.id, 
                    content_type=node.content_type)
        except AttributeError:
            # Not registered with DAG mixin
            if not graph:
                raise MissingGraphError, \
                    "Must specify graph when creating new node."
            content_type = ContentType.objects.get(
                app_label=node._meta.app_label, model=node._meta.module_name)
            return Node.objects.create(graph=graph, object_id=node.id, 
                content_type=content_type)
    
    def create(self, node_from, node_to, graph=None, combine_graphs=False):
        # Check that nodes are of correct type
        node_from = self._parse_to_node(node_from, graph)
        node_to = self._parse_to_node(node_to, graph)
        
        if not graph:
            graph = node_to.graph
        
        different_graphs = node_from.graph != node_to.graph
        if different_graphs and not combine_graphs:
            raise SeparateGraphsError
        elif different_graphs:
            node_from.graph.combine_graphs(node_to.graph)
            # Reload nodes to reflect new combined graph
            node_to = Node.objects.get(id=node_to.id)
            node_from = Node.objects.get(id=node_from.id)
            graph = node_to.graph
        
        return super(EdgeManager, self).create(graph=graph, 
            node_from=node_from, node_to=node_to)


class Edge(models.Model):
    """Edges are references, and don't have any special attributes"""
    graph = models.ForeignKey(Graph, blank=True)
    node_from = models.ForeignKey(Node, related_name="from")
    node_to = models.ForeignKey(Node, related_name="to")
    
    def save(self, *args, **kwargs):
        if self.id:
            raise NotImplementedError, \
                "Edges can only be created or deleted, not updated."
        
        if self.node_from == self.node_to:
            raise CircularReferenceError
        
        if self.node_from.graph != self.node_to.graph:
            raise SeparateGraphsError
        
        if Edge.objects.filter(node_from=self.node_from, node_to=self.node_to, 
                graph=self.graph).count():
            raise DuplicateEdgeError
        
        if not Edge.check_acyclical(self.node_from, self.node_to):
            raise CircularReferenceError
        
        kwargs["force_insert"] = True
        super(Edge, self).save(*args, **kwargs)

    objects = EdgeManager()

    def __unicode__(self):
        return "Edge from %s to %s" % (self.node_from, self.node_to)

    class Meta:
        db_table = "dag_edge"
        unique_together = ("graph", "node_from", "node_to")

    @staticmethod
    def check_acyclical(start, end):
        if start.graph != end.graph:
            raise SeparateGraphsError
        if TransitiveClosure.objects.filter(node_from=end, node_to=start, 
                graph=start.graph).count():
            return False
        else:
            return True


class TransitiveClosure(models.Model):
    t_edge_id = models.AutoField(primary_key=True)
    graph = models.ForeignKey(Graph)
    node_from = models.ForeignKey(Node, related_name="node_from")
    node_to = models.ForeignKey(Node, related_name="node_to")
    # Not foreign keys because create Edge table after syncdb, and shouldn't 
    # touch this directly anyway.
    entry_id = models.PositiveIntegerField()
    direct_id = models.PositiveIntegerField()
    exit_id = models.PositiveIntegerField()
    depth = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "dag_transitive_closure"
    
    def __unicode__(self):
        return "Transitive Closure link: %s to %s" % (self.node_from, 
            self.node_to)

