from strange_case.extensions.form_ext import HtmlTag
from types import FunctionType


class FormFieldTag(HtmlTag):
    # An alias for the 'name' property.  Used to support the View::output('input', 'name') shorthand.

    attrs = HtmlTag.attrs + [
        # The name of the surrounding form.
        'form',
        # This will be combined with the form to create a unique name="" attribute
        'name',
        # If a data or request object is available, this is the column/property that will be bound to that object.
        'column',
        # Applies a format in init_single_value()
        'format',
        # The this is either assigned explicitly or determined using data, session, or request (and possibly in conjunction with the form name)
        # For inputs that support multiple selected values, this should be an array of values.
        'value',
        # Setting errors will add error messages
        'errors',
        # Setting warnings will add warning messages
        'warnings',
        # Setting has_error to TRUE will add an 'error' class to the label.  If data is a Model object, this can be determined using has_error().
        'has_error',
        # Setting has_warning to TRUE will add a 'warning' class to the label.  If data is a Model object, this can be determined using has_warning().
        'has_warning',
        # If TRUE, it will be merged into the validation array and activate the surround_required decorator that goes around the label.
        'required',
        # The default value if value is None
        'default',
        # a Data object (Model, array) can be bound to the form.
        'data',
        # if use_session is TRUE, it will be used instead of the request object for automatic binding
        'use_session',
        # If true, disabled="disabled" will be added to the form field.
        'disabled',
        # If true, autofocus="autofocus" will be added to the form field.
        'autofocus',
        # When this is an array of two elements they will be output before and after the label tag.
        'surround_label',
        # Tabindex.
        'tabindex',
        # Generates a <label> tag.
        'label',
        # Label is on the "left" or "right"
        ('label_placement', 'left'),
        # For extra styling on the label
        'label_class',
        # When has_error is true this is added to the <label class=""> attribute
        ('label_error_class', 'error'),
        # When has_warning is true this is added to the <label class=""> attribute
        ('label_warning_class', 'warning'),
        # When has_error is true this is added to the <input class=""> attribute
        ('error_class', 'error'),
        # When has_warning is true this is added to the <input class=""> attribute
        ('warning_class', 'warning'),
        # When this is an array of two elements they will be output before and after the form field tag.
        # The surround property, inherited from HtmlTag, surrounds everything (errors, label, and form field)
        'surround_input',
        # When this is an array of two elements they will be output before and after the label tag IFF required is true.
        'surround_required',
        # If errors are displayed next to each input, instead of at the top, this will contain those error messages.
        'errors',
        # If warnings are displayed next to each input, instead of at the top, this will contain those warning messages.
        'warnings',
        # When this is an array of two elements they will be output before and after the label errors.
        'surround_errors',
        # When this is an array of two elements they will be output before and after each error.
        'surround_error',
        # Decorators are inherited from the form; if a corresponding surround option isn't available,
        'decorators',
        # form and form_id properties
        'form',
        'form_id',
    ]

    def __init__(self, name=None, **options):
        if name:
            options['name'] = name

        if options.get('enabled', None) is not None:
            options.setdefault('disabled', not options['enabled'])
        super(FormFieldTag, self).__init__(**options)

        self.check_required(name='Column or property name')

        ##|
        ##|  GLOBALS: data, form, decorators, tabindex
        ##|
        # if self.data is None:
        #   self.data = MVC::$_view.data

        # if self.form is None and MVC::$_view and MVC::$_view.form )
        #   self.form = MVC::$_view.form

        # if ! isset(self.form_id) )
        #   self.form_id = ((MVC::$_view and MVC::$_view.form_id) ? MVC::$_view.form_id : self.form)

        # if self.decorators is None and MVC::$_view and MVC::$_view.decorators )
        #   self.decorators = MVC::$_view.decorators

        # if self.tabindex is None and MVC::$_view and MVC::$_view.tabindex )
        #   self.tabindex = & MVC::$_view.tabindex

        ##|
        ##|  ENABLED
        ##|
        if self.disabled and isinstance(self.disabled, basestring) and self.disabled != '1':
            if self._class:
                self._class += u' '
            else:
                self._class = ''
            self._class += self.disabled

        #|
        #|  NAME, COLUMN.  Whether a square bracket exists and where it is determines how and if
        #|    the name is combined with the form name.
        #|  ID.  Even though it's a property of HtmlTag, it is determined here based on the name,
        #|    because name is not a property of HtmlTag.
        #|  Three scenarios, all based on the presence of a bracket, and whether form/form_id is available:
        #|  FALSE, no bracket: e.g. "the_usual"
        #|    name => form[the_usual]     OR  name => the_usual
        #|    column => the_usual             column => the_usual                  (usable w/ and w/out form/form_id)
        #|    id  => form_id_the_usual        id => the_usual
        #|  0, first char: e.g. [something][nested]
        #|    name => form[something][nested]     OR  name => [something][nested]
        #|    column => NULL                          column => NULL               (things look weird if you don't have a form/form_id)
        #|    id  => form_id_something_nested         id => _something_nested
        #|  else, exists, not first char: e.g. something[special]
        #|    name => something[special]     OR  name => something[special]
        #|    column => NULL                     column => NULL                    (form/form_id is ignored)
        #|    id  => something_special           id => something_special
        #|
        if '[' not in self.name:
            if self.column is None:
                self.column = self.name

            if self.id is None:
                self.id = (self.form_id and self.form_id + '_' or '') + self.name

            if self.form:
                self.name = "%s[%s]" % (self.form, self.name)
        else:
            bracket_pos = self.name.index('[')

            if bracket_pos == 0:
                if self.id is None:
                    self.id = (self.form_id and self.form_id or '_') + self.name.replace('[', '_').replace(']', '')
                self.name = self.form + self.name
            # else name => 'something[special]'. ignore form and form_id prefixes
            elif self.id is None:
                self.id = self.name.replace('[', '_').replace(']', '')

        #|
        #|  VALIDATION
        #|
        if'validation' in options:
            self.metadata['validation'] = options['validation']

        #|  HAS STUFF
        for property, default in {'has_error': False, 'errors': [], 'has_warning': False, 'warnings': []}.iteritems():
            if getattr(self, property) is None:
                if self.column and self.data and hasattr(self.data, property):
                    data_property = getattr(self.data, property)
                    if isinstance(data_property, FunctionType):
                        setattr(self, property, data_property(self.column))
                    else:
                        setattr(self, property, data_property)
                else:
                    setattr(self, property, default)

        #|  REQUIRED
        if self.required is None and self.metadata:
            self.required = not self.metadata.get('validation', {}).get('required', False)

    # Additional "initializor" to assign a value from the bound data or request to this input.
    def init_single_value(self):
        ##|
        ##|  VALUE
        ##|
        if self.value is not None:
            return

        if self.column and self.data:
            if hasattr(self.data, 'get'):
                if self.format is not None:
                    self.value = self.data.get(self.column, self.format)
                else:
                    self.value = self.data.get(self.column)
            elif hasattr(self.data, '__getitem__'):
                self.value = self.data[self.column]
            elif hasattr(self.data, self.column):
                self.value = getattr(self.data, self.column)
        # else:
        #     if self.form:
        #         self.value = (MVC::request(self.form) ? MVC::$_request[ self.form ][ self.column ] : NULL)
        #     else:
        #         self.value = MVC::$_request[ self.column ]

        ##|  DEFAULT
        if self.default is not None and self.value is None:
            self.value = self.default

    # SelectTag w/ multiple = true, CherryPicker, and RadioTags
    def init_multiple_value(self):
        ##|
        ##|  VALUE
        ##|
        if self.value is not None:
            return

        if self.column and self.data:
            if hasattr(self.data, 'get'):
                if self.format is not None:
                    self.value = self.data.get(self.column, self.format)
                else:
                    self.value = self.data.get(self.column)
            elif hasattr(self.data, '__getitem__'):
                self.value = self.data[self.column]
            elif hasattr(self.data, self.column):
                self.value = getattr(self.data, self.column)
        # else:
        #   if self.form:
        #       self.value = (MVC::request(self.form) ? MVC::$_request[ self.form ][ self.column ] : NULL)
        #     else
        #       self.value = MVC::$_request[ self.column ]

        #|  DEFAULT
        if self.default is not None and self.value is None:
            self.value = self.default

    # RadioTag and CheckboxTag use this instead the "editable" value in this case is the checked property, not value.
    def init_checked_value(self, compare=False):
        #|
        #|  VALUE
        #|
        if self.checked is None:
            if self.column and self.data:
                if hasattr(self.data, 'get'):
                    if self.format is not None:
                        self.checked = self.data.get(self.column, self.format)
                    else:
                        self.checked = self.data.get(self.column)
                elif hasattr(self.data, '__getitem__'):
                    self.checked = self.data[self.column]
                elif hasattr(self.data):
                    self.checked = getattr(self.data, self.column)
            # else:
            #     if self.form:
            #         self.checked = (MVC::request(self.form) ? MVC::$_request[ self.form ][ self.column ] : NULL)
            #     else:
            #         self.checked = MVC::$_request[ self.column ]

        #|  DEFAULT
        if self.default is not None and self.checked is None:
            self.checked = self.default

        #|  this.value is related to this.checked - if this.checked is a non-boolean value (like the string "is_great"), that's the value
        #|  we want sent as post data.  if it is boolean, it will be the number '1'
        if self.value is None or self.value is True:
            self.value = self.checked and self.checked is not True and self.checked or '1'

        #|  And at the end of the day, this.checked should really be a boolean, SOOO:
        #|  If we are in a RadioTag, compare checked and value:
        if compare:
            self.checked = (self.checked == self.value)
        #|  If we are in a CheckboxTag, just cast:
        else:
            self.checked = bool(self.checked)

    def output(self, **args):
        if args:
            self.set(**args)

        ret = u''
        if self.surround is not None:
            if self.surround:
                ret += self.surround[0] + u"\n"
        elif self.decorators and self.decorators['surround'] is not None:
            ret += self.decorators['surround'][0] + u"\n"

        if self.label_placement == 'right':
            ret += self.output_control()
            ret += self.output_label()
        else:  # default
            ret += self.output_label()
            ret += self.output_control()
        ret += self.output_errors()

        if self.surround is not None:
            if self.surround:
                ret += self.surround[1] + u"\n"
        elif self.decorators and self.decorators['surround'] is not None:
            ret += self.decorators['surround'][1] + u"\n"
        return ret

    def output_label(self):
        if not self.label:
            return u''
        ret = u''
        if self.surround_label is not None:
            if self.surround_label:
                ret += self.surround_label[0]
        elif self.decorators and self.decorators['surround_label'] is not None:
            ret += self.decorators['surround_label'][0]

        ret += u'<label'
        if self.id:
            ret += u' for="' + self.id + '" id="' + self.id + '_label"'
        ret += u' class="'
        if self.label_class and self.label_class:
            ret += u' ' + self.label_class
        if self.has_error and self.label_error_class:
            ret += u' ' + self.label_error_class
        if self.has_warning and self.label_warning_class:
            ret += u' ' + self.label_warning_class
        ret += u'">'
        if self.required:
            if self.surround_required is not None:
                if self.surround_required:
                    ret += self.surround_required[0]
            elif self.decorators and self.decorators['surround_required'] is not None:
                ret += self.decorators['surround_required'][0]

        ret += self.label

        if self.required:
            if self.surround_required is not None:
                if self.surround_required:
                    ret += self.surround_required[1]
            elif self.decorators and self.decorators['surround_required'] is not None:
                ret += self.decorators['surround_required'][1]

        ret += u'</label>'

        if self.surround_label is not None:
            if self.surround_label:
                ret += self.surround_label[1]
        elif self.decorators and self.decorators['surround_label'] is not None:
            ret += self.decorators['surround_label'][1]
        ret += u"\n"
        return ret

    # Outputs the input tag and surrounding decoration
    def output_control(self):
        ret = u''
        if self.surround_input is not None:
            if self.surround_input:
                ret += self.surround_input[0]
        elif self.decorators and self.decorators['surround_input'] is not None:
            ret += self.decorators['surround_input'][0]

        ret += self.output_form_field_tag()

        if self.surround_input is not None:
            if self.surround_input:
                ret += self.surround_input[1]
        elif self.decorators and self.decorators['surround_input'] is not None:
            ret += self.decorators['surround_input'][1]
        ret += u"\n"
        return ret

    def output_errors(self):
        ret = u''
        if self.errors or self.warnings:
            if self.surround_errors is not None:
                if self.surround_errors:
                    ret += self.surround_errors[0]
            elif self.decorators and self.decorators['surround_errors'] is not None:
                ret += self.decorators['surround_errors'][0]

            for warning in self.warnings:
                self.output_warning(warning)
            for error in self.errors:
                self.output_error(error)

            if self.surround_errors is not None:
                if self.surround_errors:
                    ret += self.surround_errors[1]
            elif self.decorators and self.decorators['surround_errors'] is not None:
                ret += self.decorators['surround_errors'][1]
            ret += "\n"
        return ret

    def output_warning(self, warning):
        ret = u''
        if self.surround_warning is not None:
            if self.surround_warning:
                ret += self.surround_warning[0]
        elif self.decorators and self.decorators['surround_warning'] is not None:
            ret += self.decorators['surround_warning'][0]
        ret += warning
        if self.surround_warning is not None:
            if self.surround_warning:
                ret += self.surround_warning[1]
        elif self.decorators and self.decorators['surround_warning'] is not None:
            ret += self.decorators['surround_warning'][1]
        return ret

    def output_error(self, error):
        ret = u''
        if self.surround_error is not None:
            if self.surround_error:
                ret += self.surround_error[0]
        elif self.decorators and self.decorators['surround_error'] is not None:
            ret += self.decorators['surround_error'][0]
        ret += error
        if self.surround_error is not None:
            if self.surround_error:
                ret += self.surround_error[1]
        elif self.decorators and self.decorators['surround_error'] is not None:
            ret += self.decorators['surround_error'][1]
        return ret

    def output_form_field_tag(self):
        raise NotImplementedError
