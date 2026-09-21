from django.contrib import admin
from .models import MaintenanceTicket, CalibrationLog


@admin.register(MaintenanceTicket)
class MaintenanceTicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity', 'status', 'instrument', 'telescope', 'assigned_engineer', 'created_at')
    list_filter = ('severity', 'status')
    search_fields = ('title', 'description')


@admin.register(CalibrationLog)
class CalibrationLogAdmin(admin.ModelAdmin):
    list_display = ('instrument', 'calibration_type', 'status', 'engineer', 'executed_at')
    list_filter = ('status', 'calibration_type', 'instrument')
