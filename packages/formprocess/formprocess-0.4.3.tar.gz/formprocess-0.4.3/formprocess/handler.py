""" Generic web form handler class and associates. """
import logging

from formencode import Invalid
from formencode.variabledecode import variable_decode, variable_encode
from webob.multidict import MultiDict
from webhelpers.containers import DumbObject


log = logging.getLogger(__name__)


class FormHandler(object):
    """ Base form handler. """

    use_variable_encode = False
    """ True if outgoing defaults and errors are encoded.

    Formencode's variabledecode module is used for this.
    """
    
    use_variable_decode = False
    """ True if incoming defaults are decoded.

    Formencode's variabledecode module is used for this.    
    """
    
    schema = None
    """ Object compatible with formencode's Schema.

    This object must provide a to_python method and raise Invalid exceptions
    exactly as formencode's Schema for compatibility with this library.

    By default get_schema returns this object.
    """

    def __init__(self, schema=None, use_variable_encode=None,
            use_variable_decode=None,
            update_defaults_hooks=None, get_schema_hook=None,
            update_state_hooks=None, on_process_error_hooks=None,
            defaults_filter_hooks=None, customize_fill_kwargs_hooks=None):
        """
            :param schema: This is used if there is no get_schema hook.
            :param use_variable_encode: Encode the defaults and errors using
                    formencode's variable_encode.
            :param use_variable_decode: Decode the defaults using
                    formencode's variable_decode.
            :param update_defaults_hooks: Add more defaults to the initial
                    defaults.
            :param update_state_hooks: Called to add in more attributes onto
                    the state.
            :param on_process_error_hooks: Called when an error occurs while
                    processing the form submission.
            :param defaults_filter_hooks: Call to pre-filter the defaults
                    before they are processed regardless of error or success.
            :param customize_fill_kwargs_hooks: This function is called during
                    build_form_dict so that the developer can customize the
                    fill_kwargs.
            :param get_schema_hook: This function is called to get the schema
                    for processing the defaults. There can *only* be one.
        """
        if schema is not None:
            self.schema = schema
        if use_variable_encode is not None:
            self.use_variable_encode = use_variable_encode
        if use_variable_decode is not None:
            self.use_variable_decode = use_variable_decode
        self.hooks = {
            'update_defaults': [],
            'update_state': [],
            'on_process_error': [],
            'defaults_filter': [],
            'customize_fill_kwargs': [],
            'get_schema': None
        }
        if update_defaults_hooks:
            self.hooks['update_defaults'].extend(update_defaults_hooks)
        if update_state_hooks:
            self.hooks['update_state'].extend(update_state_hooks)
        if on_process_error_hooks:
            self.hooks['on_process_error'].extend(on_process_error_hooks)
        if defaults_filter_hooks:
            self.hooks['defaults_filter'].extend(defaults_filter_hooks)
        if customize_fill_kwargs_hooks:
            self.hooks['customize_fill_kwargs'].extend(customize_fill_kwargs_hooks)
        if get_schema_hook:
            self.hooks['get_schema'] = get_schema_hook

    def have_defaults(self, form_dict):
        """ Use this to determine if the defaults have been fetched yet. """
        return 'defaults' in form_dict and form_dict['defaults'] is not None

    def was_success(self, form_dict):
        """ Use this when end_process returns the form_dict. """
        return not bool(form_dict['errors'])

    def get_schema(self, unsafe_params, state):
        """
        This method allows the developer to choose a schema at request time
        based on the submission.
        """
        if self.hooks['get_schema']:
            schema = self.hooks['get_schema'](self, unsafe_params, state)
        else:
            assert self.schema
            schema = self.schema
        return schema

    def _make_state(self, defaults, state_attrs):
        """ Makes a state object and returns it. """
        state = DumbObject(**state_attrs)
        for update_state in self.hooks['update_state']:
            update_state(self, defaults, state)
        return state
    
    def _prompt_defaults(self, state):
        """ Only called when no defaults are given to prompt(). """
        return MultiDict()

    def prompt(self, defaults=None, **state_attrs):
        """ Send the form to the user for the first time. """
        # Get state with only initial defaults.
        state = self._make_state(defaults, state_attrs)
        if defaults is None:
            defaults = self._prompt_defaults(state)
        for update_defaults in self.hooks['update_defaults']:
            defaults = update_defaults(self, defaults, state)
        if self.use_variable_encode and defaults:
            defaults = variable_encode(defaults)
        return self.build_form_dict(defaults=defaults, state=state)

    def process(self, unsafe_params, **state_attrs):
        """ Processes a form submission. """
        state = self._make_state(unsafe_params, state_attrs)
        for defaults_filter in self.hooks['defaults_filter']:
            unsafe_params = defaults_filter(self, unsafe_params, state)
        if self.use_variable_decode:
            unsafe_params = variable_decode(unsafe_params)
        schema = self.get_schema(unsafe_params, state)
        try:
            defaults = schema.to_python(unsafe_params, state=state)
        except Invalid, e:
            return self._process_invalid(e, state=state)
        form_dict = dict(defaults=defaults, errors=None, state=state)
        if not self.was_success(form_dict):
            return form_dict
        else:
            defaults, state = form_dict['defaults'], form_dict['state']
        try:
            return self.end_process(defaults, state)
        except Invalid, e:
            return self._process_invalid(e, state=state)

    def _process_invalid(self, e, state=None):
        """ Process an Invalid exception. """
        errors = e.unpack_errors(encode_variables=self.use_variable_encode)
        if self.use_variable_encode:
            defaults = variable_encode(e.value)
        else:
            defaults = e.value
        for on_process_error in self.hooks['on_process_error']:
            (defaults, errors) = on_process_error(self, defaults, errors,
                    state)
        return self.build_form_dict(defaults=defaults, errors=errors,
                state=state)

    def build_form_dict(self, defaults=None, errors=None, state=None):
        """ Build fill_kwargs with customizations and return render vars. """
        fill_kwargs = {}
        fill_kwargs['defaults'] = defaults
        fill_kwargs['errors'] = errors
        for customize_fill_kwargs in self.hooks['customize_fill_kwargs']:
            fill_kwargs = customize_fill_kwargs(self, defaults, errors, state,
                    fill_kwargs)
        return self.end_build_form_dict(defaults, errors, state, fill_kwargs)

    def end_build_form_dict(self, defaults, errors, state, fill_kwargs):
        """ Assemble the variables to be returned by prompt and process. """
        form_dict = {
            'defaults': defaults,
            'errors': errors,
            'state': state,
            'fill_kwargs': fill_kwargs,
        }
        return form_dict

    def end_process(self, defaults, state):
        """ Leave this as-is if you want to handler success/error inside
        caller of process(). """
        return self.build_form_dict(defaults=defaults, errors={},
                state=state)
