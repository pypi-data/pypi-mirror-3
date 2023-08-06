from django.contrib import admin
from webleads.models import LeadInfo, ActionType, LeadAction
from django.utils.translation import ugettext_lazy as _


class LeadInfoAdmin(admin.ModelAdmin):
    search_fields = ('full_name', 'email', )
    list_display = ('session_key', 'full_name', 'email', 'score', )


class LeadActionAdmin(admin.ModelAdmin):
    search_fields = ('lead_info__full_name', 'lead_info__email', )
    list_display = ('date', 'lead_info', 'info_user_email', 'comment',
                    'action_type', 'product_key', 'answered', )
    list_filter = ('product_key', 'action_type', 'date', 'answered',)

    def info_user_email(self, obj):
        return obj.lead_info.email
    info_user_email.short_description = _('email')


class ActionTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'score', )


admin.site.register(LeadInfo, LeadInfoAdmin)
admin.site.register(ActionType, ActionTypeAdmin)
admin.site.register(LeadAction, LeadActionAdmin)
