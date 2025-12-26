from django.db import models
from django.contrib.auth.models import User


class Arena(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="arenas",
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (owner: {self.owner.username})"


class Court(models.Model):
    arena = models.ForeignKey(
        Arena,
        on_delete=models.CASCADE,
        related_name="courts",
    )
    name = models.CharField(max_length=80)
    sport_type = models.CharField(max_length=50)
    capacity = models.PositiveIntegerField(default=10)
    indoor = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["arena_id", "name"]
        unique_together = ("arena", "name")

    def __str__(self):
        return f"{self.arena.name} - {self.name}"


class SlotTemplate(models.Model):
    """
    Weekly recurring availability.
    Example: Monday 10:00–22:00 for Court A.
    """
    court = models.ForeignKey(
        "Court",
        on_delete=models.CASCADE,
        related_name="slot_templates",
    )
    weekday = models.PositiveSmallIntegerField()  # 0=Mon ... 6=Sun
    start_time = models.TimeField()
    end_time = models.TimeField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["court_id", "weekday", "start_time"]
        unique_together = ("court", "weekday", "start_time", "end_time")
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F("start_time")),
                name="slottemplate_end_after_start",
            )
        ]

    def __str__(self):
        return f"{self.court} - {self.weekday} {self.start_time}-{self.end_time}"
