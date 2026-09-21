from django.contrib import admin
from .models import Instrument, InstrumentSensor, TelemetryLog


class InstrumentSensorInline(admin.TabularInline):
    model = InstrumentSensor
    extra = 1


@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'instrument_type', 'telescope', 'status', 'detector_temp', 'vacuum_pressure')
    list_filter = ('status', 'instrument_type', 'telescope')
    search_fields = ('name', 'code')
    inlines = [InstrumentSensorInline]


@admin.register(TelemetryLog)
class TelemetryLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'instrument', 'sensor_name', 'value', 'unit', 'status_flag')
    list_filter = ('status_flag', 'instrument')

