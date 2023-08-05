from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
#from photofile.utils import get_resolution_from_user_agent

def provide_screen_info(view_func, *args, **kwargs):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            screen_width = request.session.get('screen_width', None)
            screen_height = request.session.get('screen_height', None)
            if not screen_width or not screen_height:
                # TODO : screen_height, screen_width = get_resolution_from_user_agent(request)
                return HttpResponseRedirect('/get_screen_info/?%s' % request.get_full_path())

            return view_func(request, *args, **kwargs)
        return _wrapped_view

    if view_func is None:
        return decorator

    return decorator(view_func, *args,  **kwargs)