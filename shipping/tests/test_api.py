import json

from django.test import TestCase
from django.urls import reverse

from shipping.models import Box, Order, OrderItem, Product


class ApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = Product.objects.create(sku="BOOK", name="Book", length=20, width=13, height=3, weight=0.4)
        cls.tv = Product.objects.create(sku="TV", name="TV", length=75, width=45, height=10, weight=5.5)
        Box.objects.create(name="Small", length=25, width=20, height=10, max_weight=2, cost=1.5)
        Box.objects.create(name="Large", length=60, width=40, height=30, max_weight=15, cost=4.5)
        Box.objects.create(name="Retired", length=30, width=30, height=30, max_weight=15, cost=0.5, is_active=False)

    def post(self, data):
        return self.client.post(reverse("recommend-box"), json.dumps(data), content_type="application/json")

    def test_recommend_by_payload(self):
        r = self.post({"items": [{"sku": "BOOK", "quantity": 2}]})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["recommended_box"]["name"], "Small")

    def test_inactive_boxes_are_ignored(self):
        r = self.post({"items": [{"sku": "BOOK", "quantity": 1}]})
        self.assertNotEqual(r.json()["recommended_box"]["name"], "Retired")

    def test_no_box_fits_returns_200_with_null_box(self):
        r = self.post({"items": [{"sku": "TV"}]})
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.json()["recommended_box"])

    def test_unknown_sku_404(self):
        self.assertEqual(self.post({"items": [{"sku": "NOPE"}]}).status_code, 404)

    def test_bad_quantity_400(self):
        self.assertEqual(self.post({"items": [{"sku": "BOOK", "quantity": 0}]}).status_code, 400)
        self.assertEqual(self.post({"items": [{"sku": "BOOK", "quantity": "2"}]}).status_code, 400)

    def test_empty_items_400(self):
        self.assertEqual(self.post({"items": []}).status_code, 400)

    def test_invalid_json_400(self):
        r = self.client.post(reverse("recommend-box"), "{oops", content_type="application/json")
        self.assertEqual(r.status_code, 400)

    def test_get_not_allowed(self):
        self.assertEqual(self.client.get(reverse("recommend-box")).status_code, 405)

    def test_recommend_for_saved_order(self):
        order = Order.objects.create(reference="ORD-1")
        OrderItem.objects.create(order=order, product=self.book, quantity=1)
        r = self.client.get(reverse("order-recommend-box", args=["ORD-1"]))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["recommended_box"]["name"], "Small")

    def test_order_not_found(self):
        r = self.client.get(reverse("order-recommend-box", args=["X"]))
        self.assertEqual(r.status_code, 404)
        self.assertIn("error", r.json())

    def test_empty_saved_order_400(self):
        Order.objects.create(reference="EMPTY")
        self.assertEqual(self.client.get(reverse("order-recommend-box", args=["EMPTY"])).status_code, 400)


class IndexTests(TestCase):
    def test_root_lists_endpoints(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertIn("endpoints", r.json())
