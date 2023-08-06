import re
from django.template import Library, Node, TemplateSyntaxError
from django.core.urlresolvers import get_callable
from django.template.context import RequestContext
from django.template.response import SimpleTemplateResponse
from django.utils import simplejson
from django.utils.html import escape
from django.utils.encoding import smart_str

register = Library()

class SubViewNode(Node):
    def __init__(self, view_name, kwargs):
        self.view_name = view_name
        self.kwargs = kwargs

    def wrap(self, view_name, kwargs, text):
        params = simplejson.dumps(kwargs)
        return "<div data-subview-name='" + escape(view_name) + "' data-subview-params='" + \
               escape(params) + "'>" + text + "</div>"

    def render(self, context):
        view_name = self.view_name.resolve(context)
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
        for k, v in self.kwargs.items()])

        view = get_callable(view_name)

        if not isinstance(context, RequestContext):
            raise ValueError("subview needs RequestContext")

        if not context.has_key('request'):
            raise ValueError("subview needs request in RequestContext. " \
                + "Please add 'django.core.context_processors.request' to TEMPLATE_CONTEXT_PROCESSORS"
            )

        if hasattr(view, 'as_view'):
            view = view.as_view()

        response = view(context.get('request'), **kwargs)
        if isinstance(response, SimpleTemplateResponse):
            text = response.render().content
        else:
            text = response.content

        return self.wrap(view_name, kwargs, text)

@register.tag
def subview(parser, token):
    """
    Executes a view and inserts rendered content.
    View params can be passed as described below.

        {% subview "path.to.some_view" name1=value1 name2=value2 %}

    The first argument is a path to a view. It can be an absolute Python path
    or just ``app_name.view_name`` without the project name if the view is
    located inside the project.

    Other arguments are space-separated values that are passed to the view function.

    All arguments for the view should be present or have default values.

    For example if you have a view ``app_name.client`` taking client's id and
    the view has the following signature:

        def client(request, clientId):

    then in a template you can call the subview for a certain client like this::

        {% subview "app_name.client" clientId=client.id %}

    """
    bits = token.split_contents()
    if len(bits) < 2:
        raise TemplateSyntaxError("'%s' takes at least one argument"
                                  " (path to a view)" % bits[0])
    viewname = parser.compile_filter(bits[1])
    kwargs = {}
    kwarg_re = re.compile(r"(?:(\w+)=)?(.+)")
    bits = bits[2:]

    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to subview tag")
            name, value = match.groups()
            if name:
                kwargs[name] = parser.compile_filter(value)
            else:
                raise TemplateSyntaxError("Please provide arguments as key-value pairs to subview tag")

    return SubViewNode(viewname, kwargs)