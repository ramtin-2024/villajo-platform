# properties/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import StackedInline
from django.utils.html import format_html
from jalali_date.admin import ModelAdminJalaliMixin
from .models import (
    Property,
    Country,
    Province,
    County,
    District,
    RuralDistrict,
    City,
    PropertyLocation,
    Category,
    Amenity,
    PropertyImage,
    PropertyRule,
)


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1
    fields = (
        "image_preview",
        "image",
        "alt_text",
        "is_cover",
        "order",
    )
    readonly_fields = ("image_preview",)
    verbose_name = "تصویر"
    verbose_name_plural = "تصاویر"

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 6px;" />',
                obj.image.url,
            )
        return "—"

    image_preview.short_description = "پیش‌نمایش"


class PropertyLocationInline(StackedInline):
    model = PropertyLocation
    autocomplete_fields = ["city"]
    max_num = 1


@admin.register(Property)
class PropertyAdmin(ModelAdminJalaliMixin, ModelAdmin):
    filter_horizontal = ("amenities",)
    inlines = [PropertyLocationInline, PropertyImageInline]
    list_display = (
        "title",
        "property_type",
        "status",
        "verification_status",
        "max_guests",
        "created_at",
    )
    list_filter = (
        "property_type",
        "status",
        "verification_status",
    )
    search_fields = (
        "title",
        "description",
        "slug",
    )
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "اطلاعات هویتی",
            {"fields": ("title", "slug", "description", "property_type")},
        ),
        (
            "ظرفیت و مشخصات فیزیکی",
            {
                "fields": (
                    "max_guests",
                    "bedrooms",
                    "beds",
                    "bathrooms",
                    "toilets",
                    "building_area",
                    "land_area",
                    "floor",
                )
            },
        ),
        ("امکانات رفاهی", {"fields": ("amenities",)}),
        ("وضعیت", {"fields": ("status", "verification_status")}),
        ("تاریخ‌ها", {"fields": ("created_at", "updated_at", "published_at")}),
    )


@admin.register(Country)
class CountryAdmin(ModelAdmin):
    list_display = (
        "name",
        "code",
    )
    search_fields = (
        "name",
        "code",
    )


@admin.register(Province)
class ProvinceAdmin(ModelAdmin):
    search_fields = ["name", "code"]
    list_display = (
        "name",
        "code",
    )
    list_filter = ("country",)
    autocomplete_fields = ["country"]


@admin.register(County)
class CountyAdmin(ModelAdmin):
    search_fields = ["name", "code"]
    list_display = (
        "name",
        "code",
    )
    list_filter = ("province",)
    autocomplete_fields = ["province"]


@admin.register(District)
class DistrictAdmin(ModelAdmin):
    search_fields = ["name", "code"]
    list_display = (
        "name",
        "code",
    )
    list_filter = ("county",)
    autocomplete_fields = ["county"]


@admin.register(RuralDistrict)
class RuralDistrictAdmin(ModelAdmin):
    search_fields = ["name", "code"]
    list_display = (
        "name",
        "code",
    )
    list_filter = ("district",)
    autocomplete_fields = ["district"]


@admin.register(City)
class CityAdmin(ModelAdmin):
    search_fields = ["name", "code"]
    list_display = ("name", "code", "province", "county", "district")
    list_filter = ("province", "county", "district")
    autocomplete_fields = ["province", "county", "district"]


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    search_fields = ["name"]
    list_display = ("name", "is_active")
    list_filter = ("is_active",)


@admin.register(Amenity)
class AmenityAdmin(ModelAdmin):
    search_fields = ["name"]
    list_display = (
        "name",
        "category",
        "is_active",
    )
    list_filter = (
        "category",
        "is_active",
    )
    autocomplete_fields = ["category"]



@admin.register(PropertyRule)
class PropertyRuleAdmin(ModelAdmin):
    search_fields = [""]
