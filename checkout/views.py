from typing import ValuesView

from django.core import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import LinkSerializer
from core.models import Link,Order, OrderItem, Product
import decimal


class LinkAPIView(APIView):

    def get(self,_,code=''):
        link=Link.objects.filter(code=code).first()
        serializer=LinkSerializer(link)
        return Response(serializer.data)


class OrderAPIView(APIView):

    def post(self,request):
        data=request.data
        link=Link.objects.filter(code=data['code']).first()

        if not link:
            raise exceptions.APIException('Invalid code!')

        order=Order()
        order.user_id=link.user.id
        order.ambassador_email = link.user.email
        order.first_name = data['first_name']
        order.last_name = data['last_name']
        order.email = data['email']
        order.address = data['address']
        order.country = data['country']
        order.city = data['city']
        order.zip = data['zip']
        order.save()

        for item in data['prodcuts']:
            product = Product.objects.filter(pk=item['product_id']).first()
            quantity = decimal.Decimal(item['quantity'])

            order_item = OrderItem()
            order_item.order = order
            order_item.product_title = product.title
            order_item.price = product.price 
            order_item.quantity = quantity
            order_item.ambassador_revenue = decimal.Decimal(0.1)*product.price*quantity
            order_item.admin_revenue = decimal.Decimal(0.9)*product.price*quantity
            order_item.save()

        return Response({
            "message":"success"
        })


