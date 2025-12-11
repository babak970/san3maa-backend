from django.db import models
from django.contrib.auth.models import User


class Arena(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='arenas',
    )
    name = models.CharField(max_length=120)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Court(models.Model):
    arena = models.ForeignKey(
        Arena,
        on_delete=models.CASCADE,
        related_name='courts',
    )
    name = models.CharField(max_length=80)
    sport_type = models.CharField(max_length=50)  # futsal, basketball, etc.
    capacity = models.PositiveIntegerField(default=10)
    indoor = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.arena.name} - {self.name}"
