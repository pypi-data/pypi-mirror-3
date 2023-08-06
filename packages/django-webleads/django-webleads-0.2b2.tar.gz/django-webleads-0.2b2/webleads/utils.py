from webleads.models import LeadInfo


def get_lead_info(request):
    lead_info, created = LeadInfo.objects.get_or_create(session_key=request.session.session_key)
    return lead_info
