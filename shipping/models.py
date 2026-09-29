from django.core.validators import MinValueValidator
from django.db import models

POSITIVE = [MinValueValidator(0.0001)]


class Product(models.Model):
    """A sellable item. Dimensions in cm, weight in kg."""

    sku = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=200)
    length = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    width = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    height = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    weight = models.DecimalField(max_digits=8, decimal_places=3, validators=POSITIVE)

    def __str__(self):
        return f"{self.sku} - {self.name}"


class Box(models.Model):
    """A shipping box. Internal dimensions in cm, max_weight = max payload in kg."""

    name = models.CharField(max_length=100, unique=True)
    length = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    width = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    height = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    max_weight = models.DecimalField(max_digits=8, decimal_places=3, validators=POSITIVE)
    cost = models.DecimalField(max_digits=8, decimal_places=2, validators=POSITIVE)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "boxes"

    def __str__(self):
        return self.name


class Order(models.Model):
    reference = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.reference


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.quantity} x {self.product.sku}"
