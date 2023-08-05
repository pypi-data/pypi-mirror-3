# Utilities for working with generic relations
# From soclone project: http://code.google.com/p/soclone/source/browse/trunk/soclone/utils/models.py

from django.contrib.contenttypes.models import ContentType
import itertools

def fetch_model_dict(model, ids, fields=None):
    """
    Fetches a dict of model details for model instances with the given
    ids, keyed by their id.

    If a fields list is given, a dict of details will be retrieved for
    each model, otherwise complete model instances will be retrieved.

    Any fields list given shouldn't contain the primary key attribute for
    the model, as this can be determined from its Options.
    """
    if fields is None:
        return model._default_manager.in_bulk(ids)
    else:
        id_attr = model._meta.pk.attname
        return dict((obj[id_attr], obj) for obj
            in model._default_manager.filter(id__in=ids).values(
                *itertools.chain((id_attr,), fields)))

def populate_content_object_caches(generic_related_objects, model_fields=None):
    """
    Retrieves ``ContentType`` and content objects for the given list of
    items which use a generic relation, grouping the retrieval of content
    objects by model to reduce the number of queries executed.

    This results in ``number_of_content_types + 1`` queries rather than
    the ``number_of_generic_reL_objects * 2`` queries you'd get by
    iterating over the list and accessing each item's object attribute.

    If a dict mapping model classes to field names is given, only the
    given fields will be looked up for each model specified and the
    object cache will be populated with a dict of the specified fields.
    Otherwise, complete model instances will be retrieved.

    """
    if model_fields is None:
        model_fields = {}

    # Group content object ids by their content type ids
    ids_by_content_type = {}
    for obj in generic_related_objects:
        ids_by_content_type.setdefault(obj.content_type_id,
                                       []).append(obj.object_id)

    # Retrieve content types and content objects in bulk
    content_types = ContentType.objects.in_bulk(ids_by_content_type.keys())
    for content_type_id, ids in ids_by_content_type.iteritems():
        model = content_types[content_type_id].model_class()
        #TODO: objects is not yet defined
        objects[content_type_id] = fetch_model_dict(
            model, tuple(set(ids)), model_fields.get(model, None))

    # Set content types and content objects in the appropriate cache
    # attributes, so accessing the 'content_type' and 'object' attributes
    # on each object won't result in further database hits.
    for obj in generic_related_objects:
        obj._object_cache = objects[obj.content_type_id][obj.object_id]
        obj._content_type_cache = content_types[obj.content_type_id]