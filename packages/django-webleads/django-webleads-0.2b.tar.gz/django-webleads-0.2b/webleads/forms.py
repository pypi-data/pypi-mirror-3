# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import ugettext
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site

from webleads.models import LeadAction, ActionType


class LeadActionForm(forms.Form):
    full_name = forms.CharField(max_length=100, label=_('Full Name'))
    email = forms.EmailField()
    phone = forms.CharField(label=_('phone'), required=False, max_length=20)

    def __init__(self, request, product_key, data=None, *args, **kwargs):
        super(LeadActionForm, self).__init__(data, *args, **kwargs)
        self.request = request
        self.lead_info = request.lead_info
        self.product_key = product_key
        if data is None:
            # obtaining data from weblead if have been saved previously
            lead_full_name = self.lead_info.full_name
            lead_email = self.lead_info.email
            if lead_full_name:
                self.fields['full_name'].initial = lead_full_name
            if lead_email:
                self.fields['email'].initial = lead_email

    def base_save_action(self, action_slug, product=None, comment=None):
        action_type = ActionType.objects.get(slug=action_slug)
        LeadAction.objects.create(
            action_type=action_type,
            comment=comment,
            lead_info=self.lead_info,
            product_key=self.product_key,
        )

    def save_action(self):
        raise NotImplementedError()

    def save(self):
        self.lead_info.full_name = self.cleaned_data['full_name']
        self.lead_info.email = self.cleaned_data['email']
        self.lead_info.save()
        self.save_action()

    def _send_mail(self, comment, trans_msg):
        send_mail(
            '%s (%s)' % (comment, self.product_key),
            trans_msg % {
                'lead': self.lead_info.full_name,
                'url': 'http://%s/admin/webleads/leadaction/' % Site.objects.get_current().domain,
            },
            settings.DEFAULT_FROM_EMAIL,
            [settings.MARKETING_EMAIL],
            fail_silently=False,
        )

    def _customer_mail(self, trans_msg):
        send_mail(
            ugettext('This is the product that you request more info'),
            trans_msg % {
                'product': self.product_key,
            },
            settings.DEFAULT_FROM_EMAIL,
            [self.lead_info.email],
            fail_silently=False,
        )


class DemoRequestForm(LeadActionForm):

    def save_action(self):
        comment = ugettext('Demo request sent from web')
        self.base_save_action(
            action_slug='demo-request',
            comment=comment,
        )
        self._send_mail(comment, ugettext('There is a new demo request sent by %(lead)s. More details in %(url)s'))


class ContactRequestForm(LeadActionForm):

    def save_action(self):
        comment = ugettext('Contact request sent from web')
        self.base_save_action(
            action_slug='contact-request',
            comment=comment,
        )
        self._send_mail(comment, ugettext('There is a new contact request sent by %(lead)s. More details in %(url)s'))


class BrochureRequestForm(LeadActionForm):

    def save_action(self):
        comment = ugettext('Brochure download request sent from web')
        self.base_save_action(
            action_slug='catalog-download',
            comment=comment,
        )
        self._send_mail(comment, ugettext('There is a new brochure download request sent by %(lead)s. More details in %(url)s'))
        self._customer_mail(ugettext('You request about %(product)s, we will contact you back as soon as posible. http://www.yaco.es/media/products/%(product)s.pdf'))
