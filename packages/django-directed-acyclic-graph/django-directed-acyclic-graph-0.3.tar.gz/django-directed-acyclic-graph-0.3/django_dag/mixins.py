from django.db import models
from django.contrib.contenttypes.models import ContentType
from utils import get_objects_for_node
from models import TransitiveClosure, Node, Edge
from errors import MultipleReferencesError

class GraphMixin(models.Model):
    """Mixin class that adds methods to define, explore, and manipulate a directed acyclic graph."""
    class Meta:
        abstract = True
    
    default_graph = None
    
    @property
    def content_type(self):
        """Get Content Type for this object."""
        if not hasattr(self, "_content_type"):
            self._content_type = ContentType.objects.get(
                app_label=self._meta.app_label, model=self._meta.module_name)
        return self._content_type
    
    def node(self, graph=None):
        """Get node associated with object, if it exists. If not, return None."""
        graph = self.default_graph if not graph else graph
        node = Node.objects.filter(content_type=self.content_type, 
            object_id=self.pk)
        if graph:
            node = node.filter(graph=graph)
        if node.count() == 0:
            # Create missing node
            if not graph:
                raise ValueError("Must specify graph to create node")
            return Node.objects.create(content_type=self.content_type, 
                object_id=self.pk, graph=graph)
        elif node.count() > 1:
            raise MultipleReferencesError, "This object is associated " + \
                "with multiple nodes. Please specify the graph."
        return node[0]

    def get_parents(self, graph=None, include_self=False):
        """Get parent objects for this object."""
        graph = self.default_graph if not graph else graph
        # Shortcut for one quick SQL query with no joins
        if self.get_parent_count(graph) == 0:
            objs = []
        else:
            objs = get_objects_for_node(node=self.node(graph), 
                downwards=False, max_depth=0)
        if include_self:
            objs.insert(0, self)
        return objs
    
    def get_children(self, graph=None, include_self=False):
        """Get child objects for this object."""
        graph = self.default_graph if not graph else graph
        # Shortcut for one quick SQL query with no joins
        if self.get_child_count(graph) == 0:
            objs = []
        else:
            objs = get_objects_for_node(node=self.node(graph), max_depth=0)
        if include_self:
            objs.insert(0, self)
        return objs
    
    def get_ancestors(self, graph=None, include_self=False):
        """Get ancestor objects this object, sorted by depth."""
        graph = self.default_graph if not graph else graph
        # Shortcut for one quick SQL query with no joins
        if self.get_parent_count(graph) == 0:
            objs = []
        else:
            objs = get_objects_for_node(node=self.node(graph), 
                downwards=False)
        if include_self:
            objs.insert(0, self)
        return objs
    
    def get_descendants(self, graph=None, include_self=False):
        """Get descendant objects this object, sorted by depth."""
        graph = self.default_graph if not graph else graph
        # Shortcut for one quick SQL query with no joins
        if self.get_child_count(graph) == 0:
            objs = []
        else:
            objs = get_objects_for_node(node=self.node(graph))
        if include_self:
            objs.insert(0, self)
        return objs
    
    def get_parent_count(self, graph=None):
        """Get count of parent objects for this object."""
        graph = self.default_graph if not graph else graph
        return TransitiveClosure.objects.filter(node_from=self.node(
            graph), depth=0).count()
    
    def get_ancestor_count(self, graph=None):
        """Get count of ancestor objects for this object."""
        graph = self.default_graph if not graph else graph
        return TransitiveClosure.objects.filter(node_from=self.node(
            graph)).values("node_to").distinct().count()
    
    def get_child_count(self, graph=None):
        """Get count of child objects for this object."""
        graph = self.default_graph if not graph else graph
        return TransitiveClosure.objects.filter(node_to=self.node(
            graph), depth=0).count()
    
    def get_descendant_count(self, graph=None):
        """Get count of descendant objects for this object."""
        graph = self.default_graph if not graph else graph
        return TransitiveClosure.objects.filter(node_to=self.node(
            graph)).values("node_from").distinct().count()
    
    def is_child_node(self, graph=None):
        """Is this node a child node?"""
        graph = self.default_graph if not graph else graph
        return self.get_parent_count(graph) > 0
    
    def is_root_node(self, graph=None):
        """Is this node a root node (i.e. has no parents)?"""
        graph = self.default_graph if not graph else graph
        return self.get_parent_count(graph) == 0
    
    def is_leaf_node(self, graph=None):
        """Is this node a leaf node (i.e. has no children)?"""
        graph = self.default_graph if not graph else graph
        return self.get_child_count(graph) == 0

    def add_parent(self, obj, graph=None):
        """Add a directed link between obj (as parent) and self (as child).
        
        *obj* must be graph-aware, i.e. have a node method."""
        graph = self.default_graph if not graph else graph
        node_to = obj.node(graph=graph)
        node_from = self.node(graph=graph)
        Edge.objects.get_or_create(node_from=node_from, node_to=node_to, 
            graph=graph)

    def add_child(self, obj, graph=None):
        """Add a directed link between self (as parent) and obj (as child).
        
        *obj* must be graph-aware, i.e. have a node method."""
        graph = self.default_graph if not graph else graph
        node_to = self.node(graph=graph)
        node_from = obj.node(graph=graph)
        Edge.objects.get_or_create(node_from=node_from, node_to=node_to, 
            graph=graph)
