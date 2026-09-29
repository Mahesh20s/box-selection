# AI-Assisted Box Selection System

A small Django app that recommends the cheapest shipping box able to hold an order.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate        # Windows (cmd):  .venv\Scripts\activate
                                 # Windows (PowerShell):  .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data          # sample products, boxes, order ORD-1001
python manage.py runserver
```

Then open http://127.0.0.1:8000/ for an endpoint overview, and
http://127.0.0.1:8000/api/orders/ORD-1001/recommend-box/ for a sample result.
The POST endpoint cannot be opened in a browser (a GET returns 405); use curl, Postman or the admin-created orders instead:

```bash
curl -X POST http://127.0.0.1:8000/api/recommend-box/ -H "Content-Type: application/json" -d '{"items":[{"sku":"BOOK-1","quantity":2}]}'
```
(On Windows cmd, put the JSON in double quotes and escape inner quotes, or use Postman.)

Run the tests: `python manage.py test -v 2`

## Data model (units: cm and kg)

| Model | Key fields |
|---|---|
| `Product` | sku, name, length, width, height, weight |
| `Box` | name, internal length/width/height, max_weight (max payload), cost, is_active |
| `Order` / `OrderItem` | reference; product + quantity |

Everything is editable in the Django admin (`createsuperuser`, then `/admin/`).

## API

**`POST /api/recommend-box/`**
```json
{"items": [{"sku": "BOOK-1", "quantity": 2}, {"sku": "MUG-1"}]}
```

**`GET /api/orders/<reference>/recommend-box/`** - same result for a saved order.

Response:
```json
{
  "recommended_box": {"name": "Small", "cost": 1.5, "dimensions": [25, 20, 10]},
  "message": "ok",
  "rejected_boxes": [{"box": "Medium", "reason": "..."}],
  "placements": [{"sku": "BOOK-1", "position": [0, 0, 0], "size": [20, 13, 3]}]
}
```
If nothing fits, `recommended_box` is `null` and `message` says to split the shipment.
Errors: 400 for invalid input or an empty order, 404 for unknown SKU / order.

## How the recommendation works

Code: `shipping/services/packing.py` (pure Python, no Django imports).

For each active box:
1. **Fast rejections** with a human-readable reason: total weight over the limit, any single item that fits in no rotation, total item volume larger than the box.
2. **Packing heuristic**: a guillotine placement algorithm. Units are sorted (three orderings are tried), each is placed into the free space where it leaves the least leftover volume, in whichever of its 6 rotations fits, and the leftover space is split into three disjoint pieces.
3. **Verification**: `verify_placements` independently checks that every placement is in bounds and that nothing overlaps.

Among the boxes that pass, the **cheapest** wins; ties go to the smaller volume, then the name, so the result is deterministic.

## Assumptions and limitations (please read)

- Exact 3D bin packing is NP-hard. The heuristic is **conservative**: it never recommends a box that cannot hold the order (placements are verified), but it can reject a box that an optimal packer could have used. In that case a bigger box is recommended.
- Items only rotate in 90-degree steps. No padding, fragility, "this side up" or stacking-weight rules.
- `max_weight` is the maximum weight of the contents; the empty box's own weight is not counted.
- One box per order. If nothing fits, the API says so instead of splitting into multiple parcels.
- Floats with a small tolerance (1e-9) are used inside the packer; the database stores Decimals.
- The API has no authentication and the POST endpoint is CSRF-exempt. This is fine for a take-home, not for production.

## Tests

`shipping/tests/test_packing.py` covers cheapest-box selection, quantity, weight limits, rotation, exact-fit and just-over boundaries, tie-breaking, cost vs. size, empty/invalid input, perfect tiling of cubes, and the placement verifier.
`shipping/tests/test_api.py` covers the endpoints, validation errors, inactive boxes and saved orders.
Output of a run is in `TEST_OUTPUT.md`; CI is in `.github/workflows/tests.yml`.
