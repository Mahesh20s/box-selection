"""
Pure-Python box selection logic (no Django imports, so it is easy to unit test).

Approach
--------
Exact 3D bin packing is NP-hard, so we use a two-stage strategy per box:

1. Fast necessary checks (reject early, and give a precise reason):
   - total weight <= box.max_weight
   - every single unit fits in the box in *some* rotation
   - total item volume <= box volume

2. A constructive guillotine packing heuristic that tries to actually place every
   unit (with 90-degree rotations) inside the box. If it succeeds we get a concrete
   placement, which is independently verified by `verify_placements`.

If stage 2 fails we treat the box as "does not fit". This is conservative: we may
occasionally reject a box that a perfect packer could use, but we never recommend
a box that cannot hold the order. The cheapest box that passes is recommended.
"""
from dataclasses import dataclass, field
from itertools import permutations
from typing import List, Optional, Sequence, Tuple

EPS = 1e-9
Dims = Tuple[float, float, float]


@dataclass(frozen=True)
class Item:
    sku: str
    length: float
    width: float
    height: float
    weight: float

    @property
    def dims(self) -> Dims:
        return (self.length, self.width, self.height)

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height


@dataclass(frozen=True)
class BoxSpec:
    name: str
    length: float
    width: float
    height: float
    max_weight: float
    cost: float

    @property
    def dims(self) -> Dims:
        return (self.length, self.width, self.height)

    @property
    def volume(self) -> float:
        return self.length * self.width * self.height


@dataclass
class Placement:
    sku: str
    position: Dims  # (x, y, z) of the corner closest to the origin
    size: Dims  # oriented (dx, dy, dz)


@dataclass
class BoxEvaluation:
    box: BoxSpec
    fits: bool
    reason: str
    placements: List[Placement] = field(default_factory=list)


@dataclass
class Recommendation:
    box: Optional[BoxSpec]
    placements: List[Placement]
    evaluations: List[BoxEvaluation]
    message: str


class InvalidOrderError(ValueError):
    pass


# ---------------------------------------------------------------- helpers
def _orientations(dims: Dims):
    return set(permutations(dims))


def fits_in_some_rotation(item_dims: Dims, space: Dims) -> bool:
    return any(
        o[0] <= space[0] + EPS and o[1] <= space[1] + EPS and o[2] <= space[2] + EPS
        for o in _orientations(item_dims)
    )


def _pack(units: Sequence[Item], box_dims: Dims) -> Optional[List[Placement]]:
    """Guillotine heuristic. Returns placements for all units, or None."""
    # free spaces are (x, y, z, dx, dy, dz)
    free = [(0.0, 0.0, 0.0, *box_dims)]
    placements: List[Placement] = []

    for unit in units:
        best = None  # (leftover_volume, space_index, orientation)
        for idx, (_, _, _, sx, sy, sz) in enumerate(free):
            for o in _orientations(unit.dims):
                if o[0] <= sx + EPS and o[1] <= sy + EPS and o[2] <= sz + EPS:
                    leftover = sx * sy * sz - o[0] * o[1] * o[2]
                    if best is None or leftover < best[0] - EPS:
                        best = (leftover, idx, o)
        if best is None:
            return None

        _, idx, (w, d, h) = best
        x, y, z, sx, sy, sz = free.pop(idx)
        placements.append(Placement(unit.sku, (x, y, z), (w, d, h)))

        # Split the remaining space into three disjoint guillotine pieces.
        candidates = [
            (x + w, y, z, sx - w, sy, sz),  # slab to the right
            (x, y + d, z, w, sy - d, sz),  # slab in front
            (x, y, z + h, w, d, sz - h),  # slab on top
        ]
        free.extend(c for c in candidates if c[3] > EPS and c[4] > EPS and c[5] > EPS)

    return placements


def verify_placements(placements: Sequence[Placement], box_dims: Dims) -> bool:
    """Independent check: everything inside the box and no two items overlap."""
    for p in placements:
        for axis in range(3):
            if p.position[axis] < -EPS or p.position[axis] + p.size[axis] > box_dims[axis] + EPS:
                return False
    for i, a in enumerate(placements):
        for b in placements[i + 1:]:
            overlap = all(
                a.position[k] < b.position[k] + b.size[k] - EPS
                and b.position[k] < a.position[k] + a.size[k] - EPS
                for k in range(3)
            )
            if overlap:
                return False
    return True


# ---------------------------------------------------------------- public API
def evaluate_box(units: Sequence[Item], box: BoxSpec) -> BoxEvaluation:
    total_weight = sum(u.weight for u in units)
    if total_weight > box.max_weight + EPS:
        return BoxEvaluation(box, False, f"over weight limit ({total_weight:g} > {box.max_weight:g})")

    for u in units:
        if not fits_in_some_rotation(u.dims, box.dims):
            return BoxEvaluation(box, False, f"item {u.sku} does not fit in any orientation")

    total_volume = sum(u.volume for u in units)
    if total_volume > box.volume + EPS:
        return BoxEvaluation(box, False, "total item volume exceeds box volume")

    # Try a few orderings; the first that packs everything wins.
    orderings = [
        sorted(units, key=lambda u: u.volume, reverse=True),
        sorted(units, key=lambda u: max(u.dims), reverse=True),
        sorted(units, key=lambda u: min(u.dims), reverse=True),
    ]
    for ordering in orderings:
        placements = _pack(ordering, box.dims)
        if placements is not None and verify_placements(placements, box.dims):
            return BoxEvaluation(box, True, "fits", placements)

    return BoxEvaluation(box, False, "could not find a packing arrangement")


def recommend_box(items: Sequence[Tuple[Item, int]], boxes: Sequence[BoxSpec]) -> Recommendation:
    """
    items: sequence of (Item, quantity). Returns the cheapest box that fits.
    Ties on cost are broken by smaller volume, then by name (deterministic).
    """
    if not items:
        raise InvalidOrderError("order has no items")

    units: List[Item] = []
    for item, qty in items:
        if qty < 1:
            raise InvalidOrderError(f"quantity for {item.sku} must be >= 1")
        if min(item.dims) <= 0 or item.weight <= 0:
            raise InvalidOrderError(f"item {item.sku} has non-positive dimensions or weight")
        units.extend([item] * qty)

    evaluations = [evaluate_box(units, b) for b in boxes]
    candidates = [e for e in evaluations if e.fits]

    if not candidates:
        return Recommendation(None, [], evaluations, "No single box can hold this order; split the shipment.")

    best = min(candidates, key=lambda e: (e.box.cost, e.box.volume, e.box.name))
    return Recommendation(best.box, best.placements, evaluations, "ok")
