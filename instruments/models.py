from django.db import models
from telescopes.models import Telescope


class Instrument(models.Model):
    TYPE_SPECTROGRAPH = 'spectrograph'
    TYPE_CCD_IMAGER = 'ccd_imager'
    TYPE_IR_CAMERA = 'ir_camera'
    TYPE_PHOTOMETER = 'photometer'
    TYPE_POLARIMETER = 'polarimeter'
    TYPE_ADAPTIVE_OPTICS = 'adaptive_optics'

    TYPE_CHOICES = [
        (TYPE_SPECTROGRAPH, 'Optical Spectrograph'),
        (TYPE_CCD_IMAGER, 'Direct CCD Imager'),
        (TYPE_IR_CAMERA, 'Near-Infrared Camera'),
        (TYPE_PHOTOMETER, 'Fast Photometer'),
        (TYPE_POLARIMETER, 'Imaging Polarimeter'),
        (TYPE_ADAPTIVE_OPTICS, 'Adaptive Optics Unit'),
    ]

    STATUS_ONLINE = 'online'
    STATUS_CALIBRATING = 'calibrating'
    STATUS_STANDBY = 'standby'
    STATUS_MAINTENANCE = 'maintenance'
    STATUS_ERROR = 'error'

    STATUS_CHOICES = [
        (STATUS_ONLINE, 'Online / Science Ready'),
        (STATUS_CALIBRATING, 'Running Calibration'),
        (STATUS_STANDBY, 'Thermal Standby'),
        (STATUS_MAINTENANCE, 'Maintenance Lock'),
        (STATUS_ERROR, 'Cryo/Sensor Alarm'),
    ]

    name = models.CharField(max_length=150, help_text="Full Instrument Name.")
    code = models.CharField(max_length=20, unique=True, help_text="Short identifier code.")
    instrument_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default=TYPE_SPECTROGRAPH)
    telescope = models.ForeignKey(Telescope, on_delete=models.CASCADE, related_name="instruments", help_text="Mounted host telescope.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_STANDBY)

    # Cryogenic & Sensor Metrics
    detector_temp = models.FloatField(default=-110.5, help_text="Current CCD detector temperature (°C).")
    setpoint_temp = models.FloatField(default=-115.0, help_text="Target cooling setpoint (°C).")
    vacuum_pressure = models.FloatField(default=1.2e-6, help_text="Dewar vacuum pressure in mbar.")
    cooling_power_percent = models.FloatField(default=68.5, help_text="Cooler duty cycle percentage.")

    # Acquisition Parameters
    gain = models.FloatField(default=1.5, help_text="CCD gain in e-/ADU.")
    binning = models.CharField(max_length=10, default="1x1", help_text="Pixel binning mode (e.g., 1x1, 2x2).")
    readout_speed = models.CharField(max_length=50, default="100 kHz (Low Noise)")
    active_filter = models.CharField(max_length=50, default="V (550nm)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Instrument"
        verbose_name_plural = "Instruments"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name} [{self.get_status_display()}]"


class InstrumentSensor(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="sensors")
    sensor_name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, default="°C")
    current_value = models.FloatField()
    min_warning = models.FloatField()
    max_warning = models.FloatField()

    class Meta:
        verbose_name = "Instrument Sensor"
        verbose_name_plural = "Instrument Sensors"

    def __str__(self):
        return f"{self.instrument.code} - {self.sensor_name}: {self.current_value} {self.unit}"

    @property
    def is_warning(self):
        return self.current_value < self.min_warning or self.current_value > self.max_warning


class TelemetryLog(models.Model):
    STATUS_NORMAL = 'normal'
    STATUS_WARNING = 'warning'
    STATUS_CRITICAL = 'critical'

    FLAG_CHOICES = [
        (STATUS_NORMAL, 'Normal'),
        (STATUS_WARNING, 'Warning'),
        (STATUS_CRITICAL, 'Critical Alarm'),
    ]

    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="telemetry_logs")
    sensor_name = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=20, default="°C")
    status_flag = models.CharField(max_length=20, choices=FLAG_CHOICES, default=STATUS_NORMAL)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Telemetry Log"
        verbose_name_plural = "Telemetry Logs"
        ordering = ["-timestamp"]


class FilterWheelConfig(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name="filter_wheel")
    slot_number = models.PositiveIntegerField()
    filter_name = models.CharField(max_length=50)
    central_wavelength = models.FloatField(help_text="Central wavelength in nm.")
    bandwidth = models.FloatField(help_text="FWHM Bandwidth in nm.")

    class Meta:
        verbose_name = "Filter Wheel Slot"
        verbose_name_plural = "Filter Wheel Configurations"
        unique_together = ('instrument', 'slot_number')
        ordering = ['slot_number']

    def __str__(self):
        return f"Slot #{self.slot_number}: {self.filter_name} ({self.central_wavelength}nm)"
