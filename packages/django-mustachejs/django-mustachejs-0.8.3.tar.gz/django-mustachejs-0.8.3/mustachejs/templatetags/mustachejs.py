from django import template

from ..conf import conf
from ..loading import find, MustacheJSTemplateNotFound

from .base import BaseMustacheNode
from .mustacheraw import mustacheraw
from .mustacheich import mustacheich
from .dustjs import dustjs


register = template.Library()

register.tag(mustacheraw)
register.tag(mustacheich)
register.tag(dustjs)



class MustacheJSNode(BaseMustacheNode):
    def generate_node_text(self, resolved_name, file_content):
        output = file_content
        output = output.replace('\\', r'\\')
        output = output.replace('\n', r'\n')
        output = output.replace("'", r"\'")

        output = ("<script>Mustache.TEMPLATES=Mustache.TEMPLATES||{};"
                    + "Mustache.TEMPLATES['{0}']='".format(resolved_name)
                    + output + "';</script>")

        return output



@register.tag
def mustachejs(parser, token):
    """
    Finds the MustacheJS template for the given name and renders it surrounded by
    the requisite MustacheJS <script> tags.

    """
    bits = token.contents.split()
    if len(bits) != 2:
        raise template.TemplateSyntaxError(
            "'mustachejs' tag takes either one argument: the name/id of "
            "the template, or a pattern matching a set of templates.")
    return MustacheJSNode(*bits[1:])
