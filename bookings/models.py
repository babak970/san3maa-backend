from django.db import models
from django.contrib.auth.models import User
from arenas.models import Court


class Booking(models.Model):
    class Status(models.TextChoices):
        RESERVED = "RESERVED", "Reserved"
        CANCELLED = "CANCELLED", "Cancelled"

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="bookings",
    )
    court = models.ForeignKey(
        Court,
        on_delete=models.PROTECT,
        related_name="bookings",
    )

    start = models.DateTimeField()
    end = models.DateTimeField()

    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.RESERVED,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end__gt=models.F("start")),
                name="booking_end_after_start",
            ),
        ]

    def __str__(self):
        return f"{self.court} | {self.start}–{self.end} | {self.status}"
