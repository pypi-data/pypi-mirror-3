from visits import settings
import hashlib
import datetime

try:
    from django.utils.timezone import now
except ImportError:
    from datetime.datetime import now

def is_ignored(request, visit, url=True, bots=True, user_agents=True):
    if url:
        for ignored_url in settings.IGNORE_URLS:
            if request.META["PATH_INFO"].startswith(ignored_url):
                return True

    if user_agents and request.META.get("HTTP_USER_AGENT", "") in settings.IGNORE_USER_AGENTS:
        return True

    if bots and request.META.get("IS_BOT", False):
        return True

    if not visit.last_visit:
        return False
    elif (visit.last_visit+datetime.timedelta(minutes=settings.MIN_TIME_BETWEEN_VISITS))<now():
        return False
    else:
        return True

def gen_hash(request, *args):
    h = hashlib.sha1()
    for request_field in settings.REQUEST_FIELDS_FOR_HASH:
        h.update(request.META.get(request_field, ''))
    for arg in args:
        h.update(str(arg))
    return h.hexdigest()

def get_app_from_object(obj):
    return obj._meta.app_label

def get_model_from_object(obj):
    return obj.__class__.__name__
