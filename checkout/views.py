import stripe
from decouple import config
from django.db import transaction
from django.core import exceptions
from stripe.api_resources import line_item, payment_method, price
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

    @transaction.atomic
    def post(self,request):
        data=request.data
        link=Link.objects.filter(code=data['code']).first()

        if not link:
            raise exceptions.APIException('Invalid code!')
        try:
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
            with transaction.atomic():
                order.save()

            line_items = []

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

                line_items.append({
                    'name':product.title,
                    'description':product.description,
                    'images':[
                        product.image
                    ],
                    'amount':int(100*product*price),
                    'currency':'usd',
                    'quantity':quantity
                })

            stripe.api_key=config("STRIPE_API_KEY")

            source = stripe.checkout.Session.create(
                session_url='http://localhost:5000/success?source={CHECKOUT_SESSION_ID}',
                cancel_url='http://localhost:5000/error',
                payment_method_types=['card'],
                line_items=line_items
            )

            order.transaction_id=source['id']
            order.save()

            return Response(source)
        except Exception:
            transaction.rollback()

        return Response({
            'message':'error occured'
        })


class OrderConfirmAPIView(APIView):
    def post(self,request):
        order = Order.objects.filter(transaction_id=request.data['source']).first()

        if not order:
            raise exceptions.APIException('Order not found!')

        order.complete=True

        order.save()

        return Response({
            'message':'success'
        })


        


