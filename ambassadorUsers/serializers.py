from common.authentication import JWTAuthentication
from core.models import Link, Product
from rest_framework import serializers


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class LinkSerializer(serializers.ModelSerializer):
    
    class Meta:
        model=Link
        fields='__all__'