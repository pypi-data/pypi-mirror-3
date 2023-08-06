from django.db import models
from django.db.models import signals
from django.utils.translation import ugettext_lazy as _


class LeadInfo(models.Model):
    session_key = models.CharField(_('session key'), max_length=40,
                                   primary_key=True)
    full_name = models.CharField(_('full name'), max_length=40, blank=False,
                                null=False)
    email = models.EmailField(_('e-mail address'), blank=False, null=False)
    score = models.PositiveIntegerField(_('score'), default=0, editable=False)

    def __unicode__(self):
        return self.full_name


class ActionType(models.Model):
    slug = models.SlugField(_('action slug'))
    name = models.CharField(_('full name'), max_length=100, blank=False, null=False)
    score = models.PositiveIntegerField(_('score'))

    def __unicode__(self):
        return self.name


class LeadAction(models.Model):
    lead_info = models.ForeignKey(LeadInfo)
    product_key = models.SlugField(_('product key'))
    comment = models.TextField(_('Comment'), null=True, blank=True)
    action_type = models.ForeignKey(ActionType)
    date = models.DateTimeField(auto_now_add=True)
    phone = models.CharField(_('phone'), max_length=20, blank=True,
                            null=True)
    answered = models.BooleanField(_('awnswer sent'))

    class Meta:
        ordering = ('-date', )

    def __unicode__(self):
        return u'%s (%s)' % (self.action_type, self.comment)


def handle_saved_action(sender, **kwargs):
    lead_action, created = kwargs['instance'], kwargs['created']
    if created:
        # add the score to de weblead, depending on the action type
        lead_action.lead_info.score += lead_action.action_type.score
        lead_action.lead_info.save()


signals.post_save.connect(handle_saved_action, sender=LeadAction)
