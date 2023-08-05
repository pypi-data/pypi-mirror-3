from django.contrib import admin
from api_docs.models import *
from django.contrib.contenttypes import generic
admin.site.register(APIDoc)
admin.site.register(APIObject)
    
class APIMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'api_object', 'api_url', 'published')
    save_on_top = True
    actions = ['publish', 'un_publish']
    
    def publish(self, request, queryset):
        rows = queryset.update(published=True)
        if rows == 1:
            message_bit = "1 method was"
        else:
            message_bit = "%s methods were" % rows
        self.message_user(request, "%s successfully published." % message_bit)
        
    def un_publish(self, request, queryset):
        rows = queryset.update(published=False)
        if rows == 1:
            message_bit = "1 method was"
        else:
            message_bit = "%s methods were" % rows
        self.message_user(request, "%s successfully un-published." % message_bit)
    
    
admin.site.register(Parameter)
admin.site.register(APIMethod, APIMethodAdmin)
