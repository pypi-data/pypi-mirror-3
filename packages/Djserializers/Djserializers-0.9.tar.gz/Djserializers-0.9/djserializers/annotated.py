from functools import partial

from django.utils.encoding import smart_unicode

from .base import serialize_model, serialize_queryset


def annotate_model(obj, serialized):
    """ Add the model name and primary key. """
    return {
        "model": smart_unicode(obj._meta),
        "pk": smart_unicode(obj._get_pk_val(), strings_only=True),
        "fields": serialized,
    }


def serialize_model_annotated(obj, *args, **kwargs):
    return annotate_model(obj,
        serialize_with_annotation(obj, *args, **kwargs))


serialize_with_annotation = partial(
    serialize_model,
    handle_related=annotate_model,
)

serialize_queryset_annotated = partial(
    serialize_queryset,
    serialization_method=serialize_model_annotated,
)
