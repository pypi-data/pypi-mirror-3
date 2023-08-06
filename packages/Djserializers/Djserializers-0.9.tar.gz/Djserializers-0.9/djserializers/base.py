from functools import partial

from django.db.models.fields.related import ForeignKey, ManyToManyField
from django.utils.encoding import smart_unicode, is_protected_type

from .util import get_model_fields, get_serialization_fields


def serialize_field(obj, field):
    """
    Convert non-relational model fields.

    Protected types (i.e., primitives like None, numbers, dates,
    and Decimals) are passed through as is. All other values are
    converted to string first.
    """
    value = getattr(obj, field.name)
    if is_protected_type(value):
        return value
    else:
        return field.value_to_string(obj)


def serialize_fk(obj, field, use_natural_keys):
    """ Convert foreign key fields. """
    if use_natural_keys and hasattr(field.rel.to, "natural_key"):
        related = getattr(obj, field.name)
        return related.natural_key()
    else:
        return getattr(obj, field.get_attname())


def serialize_m2m(obj, field, use_natural_keys):
    """ Convert many-to-many fields. """
    if use_natural_keys and hasattr(field.rel.to, 'natural_key'):
        m2m_value = lambda value: value.natural_key()
    else:
        m2m_value = lambda value: smart_unicode(value._get_pk_val(), strings_only=True)
    return [m2m_value(related) for related in getattr(obj, field.name).iterator()]


def serialize_model_fields(obj, fields, related, related_fields,
        parent, use_natural_keys, handle_related):
    """ Convert a model instance to a generator. """

    for field in fields:
        if isinstance(field, ForeignKey):
            key = "%s%s" % (parent, field.name)
            if key in related:
                o = getattr(obj, field.name)
                yield field.name, handle_related(o, serialize_model(
                    obj=o,
                    fields=related_fields.get(key),
                    related=related,
                    related_fields=related_fields,
                    parent="%s__" % field.name,
                    use_natural_keys=use_natural_keys,
                ))
            else:
                yield field.name, serialize_fk(obj, field, use_natural_keys)
        elif isinstance(field, ManyToManyField):
            key = "%s%s" % (parent, field.name)
            if key in related:
                yield field.name, [handle_related(o, serialize_model(
                    obj=o,
                    fields=related_fields.get(key),
                    related=related,
                    related_fields=related_fields,
                    parent="%s__" % field.name,
                    use_natural_keys=use_natural_keys,
                )) for o in getattr(obj, field.name).all()]
            else:
                yield field.name, serialize_m2m(obj, field, use_natural_keys)
        else:
            yield field.name, serialize_field(obj, field)


def serialize_model_fields_dict(obj, fields, related, related_fields,
        parent, use_natural_keys, handle_related):
    """ Convert a model instance to a dictionary. """

    serialized = {}
    for field, value in serialize_model_fields(obj, fields, related,
            related_fields, parent, use_natural_keys, handle_related):
        serialized[field] = value
    return serialized


def serialize_model_base(obj, fields_method, model_method, fields=None,
        exclude=None, related=None, related_fields=None, parent="",
        use_natural_keys=False, handle_related=lambda x, y: y):
    """ Convert model instances to basic Python data types. """

    fields = fields_method(obj, fields=fields, exclude=exclude)
    related = related or {}
    related_fields = related_fields or {}

    return model_method(obj, fields, related, related_fields,
        parent, use_natural_keys, handle_related)


def serialize_queryset_base(queryset, serialization_method, fields=None,
        use_natural_keys=False, **kwargs):
    for obj in queryset.iterator():
        yield serialization_method(obj, fields=fields,
            use_natural_keys=use_natural_keys, **kwargs)


serialize_model = partial(
    serialize_model_base,
    fields_method=get_serialization_fields,
    model_method=serialize_model_fields_dict,
)

serialize_model_all = partial(
    serialize_model_base,
    fields_method=get_model_fields,
    model_method=serialize_model_fields_dict,
)

serialize_queryset = partial(
    serialize_queryset_base,
    serialization_method=serialize_model,
)
