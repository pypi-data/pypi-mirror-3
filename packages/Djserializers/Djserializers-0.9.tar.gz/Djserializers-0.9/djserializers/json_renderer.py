from functools import partial
from StringIO import StringIO
from types import GeneratorType

from django.utils import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder


class Encoder(DjangoJSONEncoder):

    def default(self, o):
        if isinstance(o, GeneratorType):
            return list(o)
        return super(Encoder, self).default(o)


def render_json(data, stream=None, cls=Encoder, **kwargs):
    """ Render a basic Python object to json. """
    if stream:
        json.dump(data, stream, cls=cls, **kwargs)
    return json.dumps(data, cls=cls, **kwargs)


def render_json_generator(iterable, cls=Encoder, **kwargs):
    for entry in iterable:
        yield render_json(entry, cls=cls, **kwargs)


def render_json_object_stream(iterable, stream, cls=Encoder,
        separator="\n", **kwargs):
    """ Render iterable as a stream of individual json objects. """

    for entry in render_json_generator(iterable, cls, **kwargs):
        stream.write(entry)
        stream.write(separator)


def render_json_stream(iterable, stream, cls=Encoder, **kwargs):
    """ Render iterable as a single json object stream. """
    indented = kwargs.get("indent")
    if indented:
        separator = "\n"
    else:
        separator = " "
    stream.write("[")

    first = True
    for entry in render_json_generator(iterable, cls, **kwargs):
        if not first:
            stream.write(",")
            stream.write(separator)
        stream.write(entry)
        first = False
    if indented:
        stream.write("\n")
    stream.write("]\n")


def render_to_string(iterable, method, **kwargs):
    stream = StringIO()
    method(iterable, stream, **kwargs)
    return stream.getvalue()

render_json_string = partial(render_to_string, method=render_json_stream)
render_json_object_string = partial(render_to_string, method=render_json_object_stream)
