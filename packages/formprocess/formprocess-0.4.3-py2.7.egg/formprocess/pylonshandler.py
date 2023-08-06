""" Pylons specific form handlers and schemas. """
import pylons

from formprocess.handler import FormHandler


def set_fill_encoding(handler_instance, defaults, errors, state, fill_kwargs):
    """ Set the encoding for htmlfill to use. """
    fill_kwargs.update({
        'encoding': pylons.response.determine_charset(),
    })
    return fill_kwargs


class PylonsFormHandler(FormHandler):
    """ A form handler for use with pylons. """

    def __init__(self, **kwargs):
        kwargs.setdefault('customize_fill_kwargs_hooks', []).append(set_fill_encoding)
        super(PylonsFormHandler, self).__init__(**kwargs)
