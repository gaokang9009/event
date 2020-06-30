from django.contrib import admin
from api.models import *
# Register your models here.


class OderAdmin(admin.ModelAdmin):
    list_display = ['order_code', 'count', 'user', 'event', 'ispay']


class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'type', 'user']


class UserDetailAdmin(admin.ModelAdmin):
    list_display = ['phone', 'user']


class TicketsAdmin(admin.ModelAdmin):
    list_display = ['ticket_id', 'order']


admin.site.register(UserDetail, UserDetailAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Order, OderAdmin)
admin.site.register(Tickets, TicketsAdmin)