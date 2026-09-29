from rest_framework import serializers

from .models import Booking, Payment, Villa


class VillaSerializer(serializers.ModelSerializer):
    # host نباید توسط کاربر از طریق API تعیین شود؛ در View و بر اساس
    # request.user مقداردهی می‌شود (مثلاً serializer.save(host=request.user)).
    host = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Villa
        fields = (
            "id",
            "host",
            "title",
            "capacity",
            "base_price",
            "cleaning_fee",
            "service_fee",
            "extra_guest_threshold",
            "extra_guest_fee",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class PaymentSerializer(serializers.ModelSerializer):
    # status، transaction_id و paid_at معمولاً توسط callback درگاه پرداخت
    # (نه مستقیماً توسط کاربر) تعیین می‌شوند؛ به همین دلیل read-only هستند.
    status = serializers.ChoiceField(choices=Payment.Status.choices, read_only=True)
    transaction_id = serializers.CharField(read_only=True)
    paid_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "booking",
            "amount",
            "status",
            "transaction_id",
            "payment_gateway",
            "paid_at",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate_booking(self, booking):
        request = self.context.get("request")
        if (
            request is not None
            and request.user.is_authenticated
            and booking.guest_id != request.user.id
        ):
                raise serializers.ValidationError(
                    "شما اجازه‌ی ثبت پرداخت برای این رزرو را ندارید."
                )
        return booking


class BookingSerializer(serializers.ModelSerializer):
    # guest، created_by و cancelled_by نباید مستقیماً از سمت کلاینت ست شوند؛
    # این‌ها در View بر اساس request.user (و در زمان لغو رزرو) مقداردهی می‌شوند.
    guest = serializers.PrimaryKeyRelatedField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    cancelled_by = serializers.PrimaryKeyRelatedField(read_only=True)

    # ارتباط واقعی Booking -> Payment (related_name="payments" در مدل)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Booking
        fields = (
            "id",
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
            "payments",
            "created_at",
            "updated_at",
        )
        # این فیلدها Snapshotهایی هستند که باید بر اساس منطق قیمت‌گذاری واقعی
        # پروژه (که در model.py تعریف نشده) در لایه‌ی View/Service محاسبه و
        # از طریق serializer.save(...) ست شوند، نه مستقیماً توسط کاربر.
        read_only_fields = (
            "id",
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
            "created_at",
            "updated_at",
        )

    def validate(self, attrs):
        instance = self.instance
        villa = attrs.get("villa", getattr(instance, "villa", None))
        check_in = attrs.get("check_in", getattr(instance, "check_in", None))
        check_out = attrs.get("check_out", getattr(instance, "check_out", None))
        guests_count = attrs.get(
            "guests_count", getattr(instance, "guests_count", None)
        )

        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError(
                {"check_out": "تاریخ خروج باید بعد از تاریخ ورود باشد."}
            )

        if villa and guests_count and guests_count > villa.capacity:
            raise serializers.ValidationError(
                {"guests_count": f"ظرفیت این ویلا {villa.capacity} نفر است."}
            )

        # طبق clean() مدل: میزبان نمی‌تواند برای ویلای خودش رزرو ثبت کند.
        # چون guest از request.user در View پر می‌شود، همان کاربر را با
        # host ویلا مقایسه می‌کنیم.
        request = self.context.get("request")
        if (
            villa
            and request is not None 
            and request.user.is_authenticated
        ):
            raise serializers.ValidationError(
                "میزبان  نمی تواند برای ویلای خودش رزرو ثبت کند "
            )

        # بررسی رزروهای هم‌پوشان برای همین ویلا (فقط وضعیت‌های فعال)
        if villa and check_in and check_out:
            overlapping = Booking.objects.filter(
                villa=villa,
                status__in=Booking.ACTIVE_STATUSES,
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            if instance is not None:
                overlapping = overlapping.exclude(pk=instance.pk)
            if overlapping.exists():
                raise serializers.ValidationError(
                    "این ویلا در بازه‌ی زمانی انتخاب‌شده قبلاً رزرو شده است."
                )

        return attrs

    def validate_status(self, value):
        instance = self.instance

        # هنگام ایجاد رزرو، فقط مقدار پیش‌فرض مدل (PENDING) مجاز است.
        if instance is None:
            if value != Booking.Status.PENDING:
                raise serializers.ValidationError(
                    "وضعیت اولیه‌ی رزرو باید «در انتظار پرداخت» باشد."
                )
            return value

        if value == instance.status:
            return value

        # همان منطق can_transition_to که در مدل و admin.py هم استفاده شده.
        if not instance.can_transition_to(value):
            raise serializers.ValidationError(
                f"انتقال وضعیت از «{instance.get_status_display()}» "
                "به این وضعیت مجاز نیست."
            )

        return value