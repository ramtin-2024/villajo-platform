from django.db import models

# Create your models here.
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField
from django.contrib.postgres.indexes import GistIndex
from django.contrib.postgres.operations import BtreeGistExtension


class Villa(models.Model):
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="villas"
    )

    title = models.CharField(max_length=200)

    capacity = models.PositiveIntegerField()

    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    cleaning_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0")
    )

    service_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0")
    )

    extra_guest_threshold = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    extra_guest_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Booking(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار پرداخت"
        CONFIRMED = "confirmed", "تأیید شده"
        CANCELLED = "cancelled", "لغو شده"
        EXPIRED = "expired", "منقضی شده"

    ACTIVE_STATUSES = [
        Status.PENDING,
        Status.CONFIRMED,
    ]

    villa = models.ForeignKey(
        Villa,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_bookings"
    )

    check_in = models.DateTimeField()
    check_out = models.DateTimeField()

    guests_count = models.PositiveIntegerField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # قیمت‌هایی که در لحظه‌ی رزرو ثبت می‌شوند
    nightly_price_snapshot = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    base_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    cleaning_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0")
    )

    service_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0")
    )

    extra_guest_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0")
    )

    discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0")
    )

    final_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    # Snapshot عنوان ویلا
    villa_title_snapshot = models.CharField(
        max_length=200
    )

    cancelled_at = models.DateTimeField(
        null=True,
        blank=True
    )

    cancelled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cancelled_bookings"
    )

    cancellation_reason = models.TextField(
        blank=True,
        default=""
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            GistIndex(
                fields=["villa", "check_in", "check_out"]
            ),
        ]

        constraints = [
            ExclusionConstraint(
                name="prevent_overlapping_active_bookings",
                expressions=[
                    (
                        "villa",
                        "=",
                    ),
                    (
                        models.Func(
                            models.F("check_in"),
                            models.F("check_out"),
                            function="TSTZRANGE",
                        ),
                        "&&",
                    ),
                ],
                condition=Q(
                    status__in=[
                        Status.PENDING,
                        Status.CONFIRMED,
                    ]
                ),
            ),
        ]

    def __str__(self):
        return f"{self.villa.title} - {self.guest}"

    def clean(self):
        if self.check_out <= self.check_in:
            raise ValidationError(
                "تاریخ خروج باید بعد از تاریخ ورود باشد."
            )

        if self.guests_count > self.villa.capacity:
            raise ValidationError(
                f"ظرفیت این ویلا {self.villa.capacity} نفر است."
            )

        if self.guest_id == self.villa.host_id:
            raise ValidationError(
                "میزبان نمی‌تواند برای ویلای خودش رزرو ثبت کند."
            )

    def can_transition_to(self, new_status):
        allowed_transitions = {
            self.Status.PENDING: {
                self.Status.CONFIRMED,
                self.Status.CANCELLED,
                self.Status.EXPIRED,
            },

            self.Status.CONFIRMED: {
                self.Status.CANCELLED,
            },

            self.Status.CANCELLED: set(),

            self.Status.EXPIRED: set(),
        }

        return new_status in allowed_transitions.get(
            self.status,
            set()
        )


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        PAID = "paid", "پرداخت موفق"
        FAILED = "failed", "ناموفق"

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    payment_gateway = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Payment #{self.id} - {self.amount}"