from django.conf import settings


def debug(request):
    '''
    Send the debug status to templates
    '''
    return {'DEBUG': settings.DEBUG}


def theme(request):
    '''
    Send the active interface theme to templates: "light", "dark" or
    "auto" (follow the operating system preference)
    '''
    selected = 'auto'
    try:
        user = getattr(request, 'user', None)
        if user is not None and user.is_authenticated:
            selected = user.user_settings.get_theme_name()
    except Exception:
        # error pages must render even when the database is unavailable
        selected = 'auto'
    return {'THEME': selected}


class ErrorPagesMiddleware:
    '''
    Render the styled 405 page for "method not allowed" responses
    (Django has no handler405 setting)
    '''

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get('Content-Type', '')
        if response.status_code == 405 and not settings.DEBUG \
                and content_type.startswith('text/html') \
                and not response.content:
            from .views import error_405
            allowed = response.get('Allow')
            response = error_405(request)
            if allowed:
                response['Allow'] = allowed
        return response
