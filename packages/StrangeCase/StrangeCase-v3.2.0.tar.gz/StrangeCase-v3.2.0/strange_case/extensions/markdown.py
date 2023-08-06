import jinja2
import jinja2.ext
try:
    import markdown2
except ImportError:
    from strange_case import require_package
    require_package('Markdown2')


markdowner = markdown2.Markdown()


# filter
def markdown(markdown):
    return markdowner.convert(markdown).strip()


#block
class MarkdownExtension(jinja2.ext.Extension):
    tags = set(['markdown'])

    def __init__(self, environment):
        super(MarkdownExtension, self).__init__(environment)
        environment.extend(
            markdowner=markdowner
        )

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(
            ['name:endmarkdown'],
            drop_needle=True
        )
        return jinja2.nodes.CallBlock(
            self.call_method('_markdown_support'),
            [],
            [],
            body
        ).set_lineno(lineno)

    def _markdown_support(self, caller):
        return self.environment.markdowner.convert(caller()).strip()
