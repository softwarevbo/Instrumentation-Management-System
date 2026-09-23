from django.db import models
from django.conf import settings


class SiteFeedback(models.Model):
    CATEGORY_CHOICES = [
        ('bug_error', 'Bug / System Error'),
        ('ui_ux', 'UI / UX Design Issue'),
        ('feature_req', 'Feature Request'),
        ('performance', 'System Performance'),
        ('hardware_error', 'Hardware & Telemetry Error'),
        ('other_general', 'Other / General Feedback'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('under_review', 'Under Review'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='feedbacks')
    name = models.CharField(max_length=100, blank=True, help_text="User name or Anonymous")
    email = models.EmailField(blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='other_general')
    rating = models.IntegerField(default=5, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_response = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=True, help_text="Allow feedback to be displayed in public feedback showcase")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site Feedback"
        verbose_name_plural = "Site Feedbacks"
        ordering = ["-created_at"]

    def __str__(self):
        category_label = dict(self.CATEGORY_CHOICES).get(self.category, self.category)
        return f"[{category_label}] {self.subject}"

