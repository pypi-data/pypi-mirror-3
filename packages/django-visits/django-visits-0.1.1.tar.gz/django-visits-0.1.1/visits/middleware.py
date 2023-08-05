# -*- coding: utf-8 -*-
from visits import settings
from visits.models import Visit
from visits.utils import is_ignored

class CounterMiddleware:
    def process_request(self, request):
        Visit.objects.add_uri_visit(request, request.META["PATH_INFO"])

class BotVisitorMiddleware:
    def process_request(self, request):
        user_agent = request.META["HTTP_USER_AGENT"] or None
        if user_agent in settings.IGNORE_USER_AGENTS:
            request.META.setdefault("IS_BOT", True)
        request.META.setdefault("IS_BOT", False)
