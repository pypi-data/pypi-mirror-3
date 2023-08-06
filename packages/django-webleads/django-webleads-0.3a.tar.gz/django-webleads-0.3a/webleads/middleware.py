from django.conf import settings


class LeadMiddleware(object):

    def process_request(self, request):
        if not settings.SESSION_SAVE_EVERY_REQUEST:
            session_cookie = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
            if not session_cookie:
                request.session.modified = True
        from webleads.utils import get_lead_info
        request.lead_info = get_lead_info(request)
