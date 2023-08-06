from models import *
from django.contrib import admin
from push2.models import Channel, Message, Ack


class AdminMessage(admin.ModelAdmin):
    list_display = ('sender', 'time_insert', 'text')


admin.site.register(Channel)
admin.site.register(Message, AdminMessage)
admin.site.register(Ack)
