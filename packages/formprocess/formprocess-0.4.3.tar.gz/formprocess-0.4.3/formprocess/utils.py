""" Classes and functions provided for convenience. """
from formencode import Schema, Invalid
from formencode.validators import FormValidator
from formencode.htmlfill import render as htmlfill_render
from webhelpers.html import literal
from formprocess.handler import FormHandler


class BaseSchema(Schema):
    """ Schema with sane settings. """
    allow_extra_fields = True
    filter_extra_fields = True


def get_invalid_from_errors(errors, field_dict, state):
    """ Roll dictionary of errors into an Invalid exception and return it. """
    error_list = errors.items()
    error_list.sort()
    error_message = u'<br>\n'.join([u'%s: %s' % (name, value) \
            for name, value in error_list])
    return Invalid(error_message, field_dict, state, error_dict=errors)


class BaseFormValidator(FormValidator):
    """ FormValidator with utility method. """
    
    def errors_to_invalid(self, errors, field_dict, state):
        """ Roll a dictionary of errors into Invalid exception and raise it. """
        raise get_invalid_from_errors(errors, field_dict, state)


def htmlfill(form, kwargs):
    """ Takes the html for the form and a dictionary of keyword arguments. """
    return literal(htmlfill_render(form, **kwargs))
