from django.http import HttpResponse, HttpResponseRedirect
from photofile.utils import get_resolution_from_user_agent

def provide_screen_info(request, screen_width=None, screen_height=None):
    _screen_width = request.session.get('screen_width', None)
    _screen_height = request.session.get('screen_height', None)
    if (not _screen_width or not _screen_height):
        if not screen_height and not screen_width:
            screen_height, screen_width = get_resolution_from_user_agent(request)

        if (screen_width and screen_height):
            request.session['screen_width'] = screen_width
            request.session['screen_height'] = screen_height
            return HttpResponseRedirect(request.META['QUERY_STRING'])

    html = """
    <html>
    <head>
    </head>
    <body>
    <script language="javascript">
        var query = window.location.search.substring(1);
        window.location = '/set_screen_info/' + window.screen.width + '/' + window.screen.height + '/?' + query;
    </script>
    </body>
    <html>
    """
    return HttpResponse(html)