""" Generic web form handler class and associates. """
from formprocess.handler import FormHandler


def set_fill_encoding(handler_instance, defaults, errors, state, fill_kwargs):
    """ Set the encoding for htmlfill to use. """
    request = getattr(state, 'request', None)
    fill_kwargs.update({
        'encoding': getattr(request, 'charset', 'utf-8')
    })
    return fill_kwargs


class PyramidFormHandler(FormHandler):
    """ A form handler for use with pyramid. """

    def __init__(self, **kwargs):
        kwargs.setdefault('customize_fill_kwargs_hooks', []).append(
                set_fill_encoding)
        super(PyramidFormHandler, self).__init__(**kwargs)
