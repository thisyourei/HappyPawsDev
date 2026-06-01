from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.dateparse import parse_datetime

TIMEOUT_SECONDS = getattr(settings, 'SESSION_INACTIVITY_TIMEOUT', 300)


class InactivitySessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            last_activity_str = request.session.get('last_activity')
            now = timezone.now()

            if last_activity_str:
                last_dt = parse_datetime(last_activity_str)
                if last_dt and (now - last_dt).total_seconds() > TIMEOUT_SECONDS:
                    logout(request)
                    return redirect('login')

            request.session['last_activity'] = now.isoformat()

        return self.get_response(request)
