import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Box, Order, Product
from .services.adapters import box_to_spec, product_to_item
from .services.packing import InvalidOrderError, recommend_box


def _response(rec):
    body = {
        "recommended_box": None,
        "message": rec.message,
        "rejected_boxes": [
            {"box": e.box.name, "reason": e.reason} for e in rec.evaluations if not e.fits
        ],
    }
    if rec.box:
        body["recommended_box"] = {
            "name": rec.box.name,
            "cost": rec.box.cost,
            "dimensions": [rec.box.length, rec.box.width, rec.box.height],
        }
        body["placements"] = [
            {"sku": p.sku, "position": p.position, "size": p.size} for p in rec.placements
        ]
    return JsonResponse(body)


def _run(pairs):
    boxes = [box_to_spec(b) for b in Box.objects.filter(is_active=True)]
    try:
        return _response(recommend_box(pairs, boxes))
    except InvalidOrderError as exc:
        return JsonResponse({"error": str(exc)}, status=400)


@csrf_exempt
@require_POST
def recommend_for_payload(request):
    """POST {"items": [{"sku": "ABC", "quantity": 2}, ...]}"""
    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "invalid JSON"}, status=400)

    raw_items = payload.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        return JsonResponse({"error": "'items' must be a non-empty list"}, status=400)

    pairs = []
    for row in raw_items:
        if not isinstance(row, dict) or "sku" not in row:
            return JsonResponse({"error": "each item needs a 'sku'"}, status=400)
        qty = row.get("quantity", 1)
        if not isinstance(qty, int) or isinstance(qty, bool) or qty < 1:
            return JsonResponse({"error": f"invalid quantity for {row['sku']}"}, status=400)
        try:
            product = Product.objects.get(sku=row["sku"])
        except Product.DoesNotExist:
            return JsonResponse({"error": f"unknown sku {row['sku']}"}, status=404)
        pairs.append((product_to_item(product), qty))
    return _run(pairs)


@require_GET
def recommend_for_order(request, reference):
    try:
        order = Order.objects.get(reference=reference)
    except Order.DoesNotExist:
        return JsonResponse({"error": f"unknown order {reference}"}, status=404)
    pairs = [(product_to_item(i.product), i.quantity) for i in order.items.select_related("product")]
    return _run(pairs)


@require_GET
def index(request):
    """Landing page so opening the server root in a browser shows how to use the API."""
    return JsonResponse({
        "service": "Box selection API",
        "endpoints": {
            "POST /api/recommend-box/": {"items": [{"sku": "BOOK-1", "quantity": 2}]},
            "GET /api/orders/<reference>/recommend-box/": "e.g. /api/orders/ORD-1001/recommend-box/ (after running seed_data)",
            "GET /admin/": "manage products, boxes and orders",
        },
    })
