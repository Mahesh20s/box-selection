from django.core.management.base import BaseCommand

from shipping.models import Box, Order, OrderItem, Product


class Command(BaseCommand):
    help = "Load sample products, boxes and an order for trying the API."

    def handle(self, *args, **options):
        products = [
            ("BOOK-1", "Paperback", 20, 13, 3, 0.4),
            ("MUG-1", "Ceramic mug", 10, 10, 10, 0.5),
            ("LAMP-1", "Desk lamp", 40, 15, 15, 1.2),
            ("TV-1", "32in TV", 75, 45, 10, 5.5),
        ]
        for sku, name, l, w, h, wt in products:
            Product.objects.update_or_create(
                sku=sku, defaults=dict(name=name, length=l, width=w, height=h, weight=wt)
            )
        boxes = [
            ("Small", 25, 20, 10, 2, 1.50),
            ("Medium", 40, 30, 20, 8, 2.75),
            ("Large", 60, 40, 30, 15, 4.50),
            ("Flat XL", 90, 60, 15, 20, 6.00),
        ]
        for name, l, w, h, mw, cost in boxes:
            Box.objects.update_or_create(
                name=name, defaults=dict(length=l, width=w, height=h, max_weight=mw, cost=cost)
            )
        order, _ = Order.objects.get_or_create(reference="ORD-1001")
        order.items.all().delete()
        OrderItem.objects.create(order=order, product=Product.objects.get(sku="BOOK-1"), quantity=2)
        OrderItem.objects.create(order=order, product=Product.objects.get(sku="MUG-1"), quantity=1)
        self.stdout.write(self.style.SUCCESS("Seeded. Try GET /api/orders/ORD-1001/recommend-box/"))
