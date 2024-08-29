from django.db import models


class TimeStampMixin(models.Model):
    """Mixin to add create datetime and update datetime to any model"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
