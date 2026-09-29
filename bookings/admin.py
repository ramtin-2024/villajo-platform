from django import forms
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html

from .models import Booking, BookingStatus, Payment, Villa


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = (
        "amount",
        "status",
        "transaction_id",
        "payment_gateway",
        "paid_at",
        "created_at",
    )
    readonly_fields = ("created_at",)
    can_delete = False
    show_change_link = True


@admin.register(Villa)
class VillaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "host",
        "capacity",
        "base_price",
        "cleaning_fee",
        "service_fee",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("title", "host__username", "host__email")
    autocomplete_fields = ("host",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": ("host", "title", "capacity")
        }),
        ("قیمت‌گذاری", {
            "fields": (
                "base_price",
                "cleaning_fee",
                "service_fee",
                "extra_guest_threshold",
                "extra_guest_fee",
            )
        }),
        ("تاریخ‌ها", {
            "fields": ("created_at", "updated_at"),
        }),
    )


class BookingStatusFilter(admin.SimpleListFilter):
    title = "وضعیت"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return BookingStatus.choices

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class BookingAdminForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = (
            "villa",
            "guest",
            "created_by",
            "check_in",
            "check_out",
            "guests_count",
            "status",
            "expires_at",
            "nightly_price_snapshot",
            "base_price",
            "cleaning_fee",
            "service_fee",
            "extra_guest_fee",
            "discount",
            "final_price",
            "villa_title_snapshot",
            "cancelled_at",
            "cancelled_by",
            "cancellation_reason",
        )
    def clean_status(self):
        new_status = self.cleaned_data["status"]

        # اگر رزرو تازه در حال ساخته‌شدن است (هنوز pk ندارد)،
        # محدودیت انتقال وضعیت معنا ندارد.
        if self.instance.pk is None:
            return new_status

        old_status = self.instance.status

        if old_status == new_status:
            return new_status

        if not self.instance.can_transition_to(new_status):
            raise ValidationError(
    f"انتقال وضعیت از «{self.instance.get_status_display()}» "
    f"به «{dict(BookingStatus.choices).get(new_status, new_status)}» مجاز نیست."
)

        return new_status


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm

    list_display = (
        "id",
        "villa_title_snapshot",
        "guest",
        "check_in",
        "check_out",
        "guests_count",
        "colored_status",
        "final_price",
        "created_at",
    )
    list_filter = (BookingStatusFilter, "created_at", "check_in")
    search_fields = (
        "villa__title",
        "villa_title_snapshot",
        "guest__username",
        "guest__email",
        "created_by__username",
    )
    autocomplete_fields = ("villa", "guest", "created_by", "cancelled_by")
    readonly_fields = (
        "villa_title_snapshot",
        "nightly_price_snapshot",
        "cancelled_at",
        "cancelled_by",
        "created_at",
        "updated_at",
    )
    date_hierarchy = "check_in"
    ordering = ("-created_at",)
    inlines = (PaymentInline,)
    actions = ("mark_as_confirmed", "mark_as_cancelled")

    fieldsets = (
        (None, {
            "fields": (
                "villa",
                "villa_title_snapshot",
                "guest",
                "created_by",
                "status",
            )
        }),
        ("بازه‌ی رزرو", {
            "fields": ("check_in", "check_out", "guests_count", "expires_at")
        }),
        ("قیمت‌ها", {
            "fields": (
                "nightly_price_snapshot",
                "base_price",
                "cleaning_fee",
                "service_fee",
                "extra_guest_fee",
                "discount",
                "final_price",
            )
        }),
        ("لغو رزرو", {
            # cancelled_at/cancelled_by فقط از طریق اکشن "لغو رزروهای
            # انتخاب‌شده" پر می‌شوند، نه به‌صورت دستی از فرم.
            "fields": ("cancelled_at", "cancelled_by", "cancellation_reason"),
            "classes": ("collapse",),
        }),
        ("تاریخ‌ها", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    @admin.display(description="وضعیت")
    def colored_status(self, obj):
        colors = {
            BookingStatus.PENDING: "#f59e0b",
            BookingStatus.CONFIRMED: "#16a34a",
            BookingStatus.CANCELLED: "#dc2626",
            BookingStatus.EXPIRED: "#6b7280",
        }
        color = colors.get(obj.status, "#000000")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    @admin.action(description="تأیید رزروهای انتخاب‌شده")
    def mark_as_confirmed(self, request, queryset):
        updated = 0
        skipped = 0

        for booking in queryset:
            if booking.can_transition_to(BookingStatus.CONFIRMED):
                booking.status = BookingStatus.CONFIRMED
                booking.save(update_fields=["status", "period", "updated_at"])
                updated += 1
            else:
                skipped += 1

        self.message_user(
            request,
            f"{updated} رزرو تأیید شد.",
            level=messages.SUCCESS,
        )

        if skipped:
            self.message_user(
                request,
                f"{skipped} رزرو به‌دلیل وضعیت فعلی‌شان تأیید نشدند.",
                level=messages.WARNING,
            )

    @admin.action(description="لغو رزروهای انتخاب‌شده")
    def mark_as_cancelled(self, request, queryset):
        updated = 0
        skipped = 0
        now = timezone.now()

        for booking in queryset:
            if booking.can_transition_to(BookingStatus.CANCELLED):
                booking.status = BookingStatus.CANCELLED
                booking.cancelled_at = now
                booking.cancelled_by = request.user
                booking.save(
                    update_fields=[
                        "status",
                        "period",
                        "cancelled_at",
                        "cancelled_by",
                        "updated_at",
                    ]
                )
                updated += 1
            else:
                skipped += 1

        self.message_user(request, f"{updated} رزرو لغو شد.")
        if skipped:
            self.message_user(
                request,
                f"{skipped} رزرو به‌دلیل وضعیت فعلی‌شان لغو نشدند.",
                level="warning",
            )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "booking",
        "amount",
        "status",
        "payment_gateway",
        "transaction_id",
        "paid_at",
        "created_at",
    )
    list_filter = ("status", "payment_gateway", "created_at")
    search_fields = (
        "transaction_id",
        "booking__villa_title_snapshot",
        "booking__guest__username",
    )
    autocomplete_fields = ("booking",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)
