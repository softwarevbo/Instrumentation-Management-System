from django.contrib import admin
from .models import Telescope, TelescopeLog


@admin.register(Telescope)
class TelescopeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'aperture', 'mount_type', 'status', 'dome_status', 'right_ascension', 'declination')
    list_filter = ('status', 'mount_type', 'dome_status')
    search_fields = ('name', 'code', 'location')


@admin.register(TelescopeLog)
class TelescopeLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'telescope', 'event_type', 'user', 'message')
    list_filter = ('event_type', 'telescope')
    search_fields = ('message', 'telescope__code')
