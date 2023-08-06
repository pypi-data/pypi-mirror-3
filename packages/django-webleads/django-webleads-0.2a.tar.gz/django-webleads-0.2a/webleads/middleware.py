class LeadMiddleware(object):

    def process_request(self, request):
        from webleads.utils import get_lead_info
        request.lead_info = get_lead_info(request)
