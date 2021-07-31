
from rest_framework import generics,mixins, serializers
from rest_framework import response
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .serializers import OrderSerializer, ProductSerializer,LinkSerializer
from common.serializers import UserSerializer
from core.models import Link, Order, Product, User
from common.authentication import JWTAuthentication
from django.core.cache import cache


class AmbassadorAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]

    def get(self,_):
        ambassadors = User.objects.filter(is_ambassador=True)
        serializer = UserSerializer(ambassadors,many=True)
        return Response(serializer.data)


class ProductGenericAPIView(generics.GenericAPIView,mixins.RetrieveModelMixin,mixins.ListModelMixin):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class=ProductSerializer

    def get(self,request,pk=None):
        if pk:
            return self.retrieve(request,pk)
        
        return self.list(request)

    
    def post(self,request):
        response = self.create(request)
        for key in cache.keys('*'):
            if 'products_frontend' in key:
                cache.delete(key)
        cache.delete('products_backend')
        return response

    def put(self,request,pk=None):
        response = self.partial_update(request,pk)
        for key in cache.keys('*'):
            if 'products_frontend' in key:
                cache.delete(key)
        cache.delete('products_backend')
        return response

    def delete(self,request,pk=None):
        response = self.destroy(request,pk)
        for key in cache.keys('*'):
            if 'products_frontend' in key:
                cache.delete(key)
        cache.delete('products_backend')
        return response


class LinkAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]

    def get(self,request,pk=None):
        links=Link.objects.filter(user_id=pk)
        serializer = LinkSerializer(links,many=True)
        return Response(serializer.data)


class OrderAPIView(APIView):
    authentication_classes=[JWTAuthentication]
    permission_classes=[IsAuthenticated]

    def get(self,request):
        orders = Order.objects.filter(complete=True)
        serializer=OrderSerializer(orders,many=True)

        return Response(serializer.data)