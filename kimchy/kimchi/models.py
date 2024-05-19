from django.db import models


class Menu(models.Model):
    dish = models.CharField(max_length=100)
    image = models.CharField(max_length=300, default="http")
    ingredients = models.CharField(max_length=100)
    price = models.CharField(max_length=60)
    availability = models.BooleanField(default=False)


class Order(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    food = models.CharField(max_length=100)
    quantity = models.CharField(max_length=100)
    delivery_status = models.BooleanField(default=False)


