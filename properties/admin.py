# properties/admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.admin import StackedInline
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
)


class PropertyLocationInline(StackedInline):
    model = PropertyLocation
    autocomplete_fields = ["city"]


@admin.register(Property)
class PropertyAdmin(ModelAdminJalaliMixin,ModelAdmin):
    inlines = [PropertyLocationInline]
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


