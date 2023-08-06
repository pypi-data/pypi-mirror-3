from functools import wraps


def lead_action(action_type_slug=None, product_key=None):
    """
    Decorator that executes an action for the lead, which will increase the lead
    scoring.

    The action executed will be a new action of the passed ``action_type_slug``,
    and will be recorded for ``product_key`` product.

    Usage::

        from django.http import HttpResponse

        from webleads.decorators import lead_action

        @lead_action('demo-request', 'uniquid')
        def do_demo_request(request):
            return HttpResponse('demo submitted')
    """
    def _lead_action(viewfunc):
        def _lead_action_inner(request, *args, **kw):
            response = viewfunc(request, *args, **kw)
            from webleads.models import ActionType, LeadAction
            action_type = ActionType.objects.get(slug=action_type_slug)
            LeadAction.objects.create(
                action_type=action_type,
                comment='',
                lead_info=request.lead_info,
                product_key=product_key,
            )
            return response
        return wraps(viewfunc)(_lead_action_inner)
    return _lead_action
