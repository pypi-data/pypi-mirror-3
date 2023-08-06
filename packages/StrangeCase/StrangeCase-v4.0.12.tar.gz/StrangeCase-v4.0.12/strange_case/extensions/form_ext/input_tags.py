import json
from strange_case.extensions.form_ext import FormFieldTag, entitize, deentitize


class InputTag(FormFieldTag):
    attrs = FormFieldTag.attrs + [
        #Readonly attribute
        'readonly',
        #Used to disable autocompletion on inputs that should not intuitively use that browser feature.
        'autocomplete',
        #Fixes the length using maxlength="" attribute.
        'maxlength',
        #Used on text inputs to encode raw html.
        'double_encode',
        #HTML5 placeholder attribute.
        'placeholder',
        #Used w/ <input type="number" />
        'step',
        #Stores the type="" attribute so that all the InputTags can share an outputControl method.
        'type',
    ]

    def __init__(self, *args, **options):
        if 'type' not in options and type(self) != InputTag:
            options['type'] = type(self)._type
        super(InputTag, self).__init__(*args, **options)
        if type(self) == InputTag:
            self.check_required('type')

        self.init_single_value()

        # translate autocomplete to its correct html values
        if self.autocomplete:  # truthy
            self.autocomplete = 'on'
        elif self.autocomplete is not None:  # falsy, except "not set"
            self.autocomplete = 'off'

    def output_form_field_tag(self):
        """
        Outputs the input tag and surrounding decoration
        """
        if self.tabindex is not None:
            tabindex = self.tabindex
            self.tabindex += 1
        else:
            tabindex = None
        return '<input' +\
            ' type="' + self.type + '"' +\
            (self.metadata and ' data-meta="' + entitize(json.dumps(deentitize(self.metadata))) + '"' or '') +\
            (self.style and ' style="' + self.style + '"' or '') +\
            (self.name and ' name="' + self.name + '"' or '') +\
            (self.id and ' id="' + self.id + '"' or '') +\
            (self.title and ' title="' + self.title + '"' or '') +\
            ' class="' + (self._class and ' ' + self._class or '') +\
                         (self.has_error and self.error_class and ' ' + self.error_class or '') +\
                         (self.has_warning and self.warning_class and ' ' + self.warning_class or '') + '"' +\
            ' value="' + entitize(self.value) + '"' +\
            (tabindex is not None and ' tabindex="' + tabindex + '"' or '') +\
            (self.maxlength and ' maxlength="' + self.maxlength + '"' or '') +\
            (self.autocomplete and ' autocomplete="' + self.autocomplete + '"' or '') +\
            (self.placeholder and ' placeholder="' + self.placeholder + '"' or '') +\
            (self.step and ' step="' + self.step + '"' or '') +\
            (self.disabled and ' disabled="disabled"' or '') +\
            (self.autofocus and ' autofocus="autofocus"' or '') +\
            (self.readonly and ' readonly="readonly"' or '') +\
            ' />'


class InputTextTag(InputTag):
    _type = 'text'

    def create(*more_options, **options):
        args = []
        for arg in more_options:
            if isinstance(arg, basestring):
                args.append(arg)
            else:
                options.update(more_options)
        return InputTextTag(*args, **options)
