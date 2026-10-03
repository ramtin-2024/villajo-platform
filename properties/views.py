from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from properties.models import Property
from properties.serializers import (
    PropertyCreateSerializer,
    PropertyDetailSerializer,
    PropertyListSerializer,
    PropertyUpdateSerializer,
)


@api_view(["GET"])
def property_list(request):
    if request.method == "GET":
        properties = Property.objects.all()
        serializer = PropertyListSerializer(properties, many=True)
        return Response(serializer.data)


@api_view(["POST"])
def property_create(request):
    if request.method == "POST":
        serializer = PropertyCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
def property_detail(request, pk):
    try:
        properties = Property.objects.get(pk=pk)
    except Property.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = PropertyDetailSerializer(properties)
        return Response(serializer.data)

    elif request.method == "PUT":
        serializer = PropertyUpdateSerializer(properties, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "PATCH":
        serializer = PropertyUpdateSerializer(
            properties, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        properties.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
