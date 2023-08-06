# -*- encoding: utf-8 -*-

html_escape_table = (
    (u"\"", "&quot;"),
    (u"'", "&#039;"),
    (u"<", "&lt;"),
    (u">", "&gt;"),
    (u">", "&gt;"),
)


def entitize(string):
    if not string:
        return u''
    string = string.replace(u'&', u'&amp;')
    for c, esc in html_escape_table:
        string = string.replace(c, esc)
    return string


def deentitize(string):
    if not string:
        return u''
    for k in html_escape_table:
        v = html_escape_table[k]
        string = string.replace(v, k)
    string = string.replace(u'&amp;', u'&')
    return string


class HtmlTag(object):
    """
    The HtmlTag and its child classes are used in Jinja to create
    tags with dynamic attributes, most notably form field tags.
    """
    attrs = [
        # Generates a title="" attribute.  Provides additional information about the tag.
        'title',
        # Creates the class="" attribute.
        '_class',
        # Creates the style="" attribute.
        'style',
        # Creates the id="" attribute.
        'id',
        # Creates the data-meta="" attribute.
        'metadata',
        # When this is an array of two elements they will be output before and after the tag.
        'surround',
    ]
    registry = {}

    def output(self):
        """
        Returns the html tag contents
        """
        raise NotImplementedError('HtmlTag.output')

    def __init__(self, **options):
        for property in type(self).attrs:
            if isinstance(property, tuple) or isinstance(property, list):
                default = property[1]
                property = property[0]
            else:
                default = None
            setattr(self, property, default)

        for property, value in options.iteritems():
            if hasattr(self, property):
                setattr(self, property, value)

    @classmethod
    def register(self, tag, _HtmlTagClass):
        self.register[tag] = _HtmlTagClass

    @classmethod
    def factory(self, tag, **options):
        if tag not in self.registry:
            raise KeyError('Unknown tag "%s"' % tag)
        return self.registry[tag](**options)

    def set(self, *args, **properties):
        """
        Convenient for chaining.  Supports a single property, value pair or an array of property => value pairs::

            LinkTag::create() \
              .set('href', 'http://website.com/') \
              .set(rel='external') \
              .output()
        """
        if len(args) == 2:
            properties.update({args[0]: args[1]})
        elif args:
            raise TypeError('Only two arguments, or a **dict, are valid values to HtmlTag.set')
        for property, value in properties.iteritems():
            if hasattr(self, property):
                setattr(self, property, value)
        return self

    def check_required(self, *properties, **messages):
        """
        Throws an exception when a required option was not included.
        """
        errors = {}
        for property in properties:
            if not hasattr(self, property) or getattr(self, property) is None:
                errors[property] = u'%s: Required' % property

        for property, message in messages.iteritems():
            # None doesn't count here!
            if not hasattr(self, property) or getattr(self, property) is None:
                errors[property] = u'%s: %s' % (property, message)
        if errors:
            raise TypeError(
                'The following {property} required: "{required}"\n{details}'.format(
                    property=len(errors) == 1 and 'property is' or 'properties are',
                    required='", "'.join(errors.keys()),
                    details="\n".join(errors.values()),
                    ))

    def __str__(self):
        """
        Returns the output
        """
        return self.output()
