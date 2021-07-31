from django.core.management import BaseCommand

from random import randrange
from faker import Faker
from core.models  import Product

class Command(BaseCommand):
    def handle(self,*args,**kwargs):
        faker = Faker()

        for _ in range(30):
            Product.objects.create(
                title=faker.name(),
                description=faker.text(),
                image=faker.image_url(),
                price=randrange(10,100)
            )
            