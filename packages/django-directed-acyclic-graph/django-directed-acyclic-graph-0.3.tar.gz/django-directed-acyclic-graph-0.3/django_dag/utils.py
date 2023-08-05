from django.contrib.contenttypes.models import ContentType
from django.db import connection, transaction
from errors import CircularReferenceError, SeparateGraphsError, \
    DuplicateEdgeError
from sql import sql

UPWARDS = """select min(tc.depth) as depth, n.id as node_id, n.content_type_id, n.object_id 
    from dag_node as n
    inner join dag_transitive_closure as tc
    on n.id = tc.node_to_id 
    where tc.node_from_id = %s
        and tc.depth <= %s 
    group by n.id, n.content_type_id, n.object_id, tc.depth
    order by tc.depth"""

DOWNWARDS = """select min(tc.depth) as depth, n.id as node_id, n.content_type_id, n.object_id 
        from dag_node as n
        inner join dag_transitive_closure as tc
        on n.id = tc.node_from_id 
        where tc.node_to_id = %s
            and tc.depth <= %s 
        group by n.id, n.content_type_id, n.object_id, tc.depth
        order by tc.depth"""

def flatten(x):
    """Flattened a set of iterables into a single list.
    
    From http://kogs-www.informatik.uni-hamburg.de/~meine/python_tricks"""
    result = []
    for el in x:
        if hasattr(el, '__iter__') and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result

def get_objects_for_node(node, max_depth=9999, downwards=True, 
        sort_reverse=False, using="default"):
    """Take a Node and an optional maximum depth, and return a list of model objects linked by generic keys and sorted by depth. 

    Borrows heavily from http://code.google.com/p/soclone/source/browse/trunk/soclone/utils/models.py"""
    if not node:
        # Can be called by get_children, etc., when node isn't created.
        return ()
    query = DOWNWARDS if downwards else UPWARDS
    # Realize generator with list comprehension
    tc_query = [obj for obj in sql(query, (node.id, max_depth), using=using, 
        as_dict=True)]

    # Create dictionary with content type ids as keys, and objects ids as 
    # values
    content_type_dict = {}
    blank_nodes = []
    for obj in tc_query:
        if obj['content_type_id']:
            content_type_dict.setdefault(obj['content_type_id'], 
                []).append(obj['object_id']) 
        else: # Blank content type
            blank_nodes.append((obj['node_id'], obj['depth']))

    # Create dictionary linking (object_id, content_type) to depth
    depth_dict = dict([((obj['content_type_id'], obj['object_id']), 
        obj['depth']) for obj in tc_query]) 

    # Get queryset per content type, and aggregate together
    content_types = ContentType.objects.filter(id__in=content_type_dict.keys( 
        ))
    objs = flatten([create_objects_iterable_with_depth(c, content_type_dict, 
        depth_dict) for c in content_types])
    
    # Add nodes without content types
    from models import Node
    blank_nodes_queryset = Node.objects.filter(id__in=[x[0] for x in \
        blank_nodes])
    for index, node in enumerate(blank_nodes_queryset):
        node._depth = blank_nodes[index][1]
        objs.append(node)
    
    objs = sort_by_attribute(objs, "_depth", sort_reverse=sort_reverse)
    return objs

def create_objects_iterable_with_depth(content_type, content_type_dict, 
        depth_dict):
    model = content_type.model_class()
    objs = model.objects.filter(id__in=content_type_dict[content_type.id])
    for obj in objs:
        # Add depth
        obj._depth = depth_dict[(content_type.id, obj.id)]
    return objs

def create_objects_iterable(content_type, content_type_dict):
    model = content_type.model_class()
    return model.objects.filter(id__in=content_type_dict[content_type.id])

def sort_by_attribute(lst, attr, sort_reverse=False):
    """Sort a list of objects based on an attribute.
    
    Falls back on list index if attributes are equal.
    Based on http://code.activestate.com/recipes/52230/"""
    intermed = [ (getattr(obj,attr), index, obj) for index, obj in enumerate(
        lst)]
    intermed.sort(reverse = sort_reverse)
    return [ tup[-1] for tup in intermed ]