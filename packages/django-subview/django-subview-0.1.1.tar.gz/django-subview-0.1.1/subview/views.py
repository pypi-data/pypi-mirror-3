
def subview_handler(request, view_name, json_params):
    from django.core.urlresolvers import get_callable
    from django.utils import simplejson

    view = get_callable(view_name)
    if hasattr(view, 'as_view'):
        view = view.as_view()

    import logging
    logger = logging.getLogger('django')
    logger.info(json_params)

    if json_params == '':
        kwargs = {}
    else:
        kwargs = simplejson.loads(json_params)

    return view(request, **kwargs)