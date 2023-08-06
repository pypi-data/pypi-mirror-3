def get_model_fields(model, fields=None, exclude=None):
    """
    Returns a generator of fields for a model.

    Arguments::

        ``fields`` is an optional list to return only those field names.
        ``exclude`` is an optional list to exclude field names.
    """
    opts = model._meta
    for field in sorted(opts.fields + opts.many_to_many):
        if fields and not field.name in fields:
            continue

        if exclude and field.name in exclude:
            continue

        yield field


def get_serialization_fields(model, fields=None, exclude=None):
    """
    Returns filtered field set.

    Fields with serialize set to false, and manually created M2M
    fields are excluded by default unless specified in the fields
    argument.
    """
    fields = fields or []
    exclude = exclude or []

    for field in get_model_fields(model, fields, exclude):
        if not field.serialize and not field.name in fields:
            continue

        if field.rel and hasattr(field.rel, "through"):
            if not field.rel.through._meta.auto_created:
                if not field.name in fields:
                    continue

        yield field
