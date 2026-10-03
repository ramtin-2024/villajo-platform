from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from properties.views import (
    property_create,
    property_detail,
    property_list,
)

urlpatterns = [
    path("properties/", property_list, name="property-list"),
    path("properties/create/", property_create, name="property-create"),
    path("properties/<int:pk>/", property_detail, name="property-detail"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
