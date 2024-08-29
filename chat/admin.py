from django.contrib import admin, messages
from django.http import HttpResponseRedirect

# Register your models here.
from chat.models import Message, Thread


class ThreadAdmin(admin.ModelAdmin):
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        try:
            return super(ThreadAdmin, self).changeform_view(request, object_id, form_url, extra_context)
        except Exception as e:
            self.message_user(request, e, level=messages.ERROR)
            return HttpResponseRedirect(request.path)


admin.site.register(Message)
admin.site.register(Thread, ThreadAdmin)
