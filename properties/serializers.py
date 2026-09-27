from rest_framework import serializers

from .models import (
    Amenity,
    CancellationPolicy,
    CancellationRule,
    Category,
    City,
    Country,
    County,
    District,
    PermissionRule,
    Property,
    PropertyImage,
    PropertyLocation,
    PropertyRule,
    PropertyVerification,
    Province,
    QuantityRule,
    RuralDistrict,
    TimeRule,
)


# ==================================================
#     Key Accommodation Information
# ==================================================
class PropertyListSerializer(serializers.ModelSerializer):
    property_type_display = serializers.CharField(
        source="get_property_type_display",
        read_only=True
    )
    class Meta:
        model = Property
        fields = (
            "id",
            "title",
            "description",

            "property_type",
            "property_type_display",

            "max_guests",
            "bedrooms",
            "beds",
            "bathrooms",
            "toilets",

            "building_area",
            "land_area",
            "floor",

            "status",
            "verification_status",

            "created_at",
            "updated_at",
            "published_at",
        )

        read_only_fields = (
            "id",
            "status",
            "verification_status",
            "created_at",
            "updated_at",
            "published_at",
        )

# ===================================================
#                   Location
# ===================================================
class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model =  Country
        fields = ("id","name","code","slug")
        read_only_fields =("id") 

class ProvinceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Province
        fields = ("id","name","code","slug","country")
        read_only_fields =("id")

class CountySerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = ("id","name","code","slug","province")
        read_only_fields =("id")

class  DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ("id","name","code","slug","county")
        read_only_fields =("id") 

class RuralDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuralDistrict
        fields = ("id","name","code","slug","district")
        read_only_fields =("id")

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ("id","name","code","slug","province","county","district")
        read_only_fields =("id")
class PropertyLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyLocation
        fields = ("id","address","postal_code","latitude","longitude","property_obj","city")
        read_only_fields = ("id", "property_obj")


# ==================================================
#                       Amenity
# ==================================================
class CategorySerializer(serializers.ModelSerializer):
    class Meta : 
        model = Category
        fields = ("id","name","is_active","slug")
        read_only_fields =("id")
class AmenityNestedSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Amenity
        fields = (
            "id",
            "name",
            "slug",
        )
        read_only_fields =("id")

class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields=("id","image","alt_text","is_cover","order","created_at","updated_at","property_obj")
        read_only_fields =("id","property_obj","created_at","updated_at")  

# ===================================================
#                Laws and regulations
# ===================================================
class PropertyRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyRule
        fields =("id","rule_key","property_obj","amenity")
        read_only_fields = ("id",)

class PermissionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionRule
        fields = ("id","allowed","rule")
        read_only_fields = ("id",)

class TimeRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeRule
        fields =("id","start_time","end_time","rule")
        read_only_fields = ("id",)   

class QuantityRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuantityRule
        fields = ("id","value","rule")
        read_only_fields = ("id",)            
# ===================================================
#               Cancellation Policies
# ===================================================
class CancellationPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationPolicy
        fields = ("id","title","description","is_active","created_at","updated_at","property_obj")
        read_only_fields = (
            "id",
            "property_obj",
            "created_at",
            "updated_at",
        )

class CancellationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancellationRule
        fields = ("id","hours_before_checkin","hours_before_checkin_max","refund_percentage","charge_first_night","note","priority","policy") 
        read_only_fields = ("id",)     
# ====================================================
#         Accommodation Verification Status
# ====================================================
class PropertyVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyVerification
        fields= ("id", "status","verified_at","rejection_reason","admin_note","created_at","updated_at","property_obj") 
        read_only_fields = (
            "id",
            "status",
            "verified_at",
            "created_at",
            "updated_at",
            "property_obj",
        )         