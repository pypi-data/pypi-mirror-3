from django.conf import settings

def settings_context(context):
    return {'MEDIA_URL': settings.MEDIA_URL, 'MEDIA_ROOT': settings.MEDIA_ROOT }