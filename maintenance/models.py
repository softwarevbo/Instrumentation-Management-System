from django.db import models
from django.conf import settings
from instruments.models import Instrument
from telescopes.models import Telescope


class MaintenanceTicket(models.Model):
    SEVERITY_CRITICAL = 'critical'
    SEVERITY_HIGH = 'high'
    SEVERITY_MEDIUM = 'medium'
    SEVERITY_LOW = 'low'

    SEVERITY_CHOICES = [
        (SEVERITY_CRITICAL, 'CRITICAL - System Halt'),
        (SEVERITY_HIGH, 'HIGH - Science Impact'),
        (SEVERITY_MEDIUM, 'MEDIUM - Degraded Mode'),
        (SEVERITY_LOW, 'LOW - Routine / Scheduled'),
    ]

    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_CLOSED, 'Closed'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Detailed description of the fault or maintenance required.")
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_MEDIUM)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    instrument = models.ForeignKey(Instrument, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets")
    telescope = models.ForeignKey(Telescope, on_delete=models.SET_NULL, null=True, blank=True, related_name="tickets")
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="reported_tickets")
    assigned_engineer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")
    resolution_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Maintenance Ticket"
        verbose_name_plural = "Maintenance Tickets"
        ordering = ['-created_at']

    def __str__(self):
        target = self.instrument or self.telescope
        return f"[{self.get_severity_display()}] {self.title} → {target}"

    @property
    def severity_color(self):
        return {
            'critical': '#ef4444',
            'high': '#f97316',
            'medium': '#f59e0b',
            'low': '#10b981',
        }.get(self.severity, '#64748b')


class CalibrationLog(models.Model):
    CAL_TYPE_CHOICES = [
        ('bias', 'Bias Frame'),
        ('dark', 'Dark Frame'),
        ('flat', 'Flat Field'),
        ('wavelength', 'Wavelength Calibration Lamp'),
        ('standard_star', 'Standard Star Flux Calibration'),
        ('focus', 'Focus / PSF Calibration'),
        ('pointing', 'Pointing Model Calibration'),
    ]

    CAL_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="calibrations")
    calibration_type = models.CharField(max_length=30, choices=CAL_TYPE_CHOICES)
    standard_lamp_or_target = models.CharField(max_length=100, blank=True, help_text="Arc lamp ID, standard star name, or flat source.")
    engineer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="calibrations_run")
    status = models.CharField(max_length=20, choices=CAL_STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Calibration Log"
        verbose_name_plural = "Calibration Logs"
        ordering = ['-executed_at']

    def __str__(self):
        return f"{self.instrument.code} | {self.get_calibration_type_display()} [{self.get_status_display()}]"
