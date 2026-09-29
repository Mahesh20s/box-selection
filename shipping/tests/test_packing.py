from django.test import SimpleTestCase

from shipping.services.packing import (
    BoxSpec, InvalidOrderError, Item, Placement, evaluate_box, recommend_box,
    verify_placements,
)

SMALL = BoxSpec("Small", 25, 20, 10, 2, 1.5)
MEDIUM = BoxSpec("Medium", 40, 30, 20, 8, 2.75)
LARGE = BoxSpec("Large", 60, 40, 30, 15, 4.5)
BOXES = [LARGE, SMALL, MEDIUM]  # deliberately unordered

BOOK = Item("BOOK", 20, 13, 3, 0.4)
MUG = Item("MUG", 10, 10, 10, 0.5)
TV = Item("TV", 75, 45, 10, 5.5)


class RecommendationTests(SimpleTestCase):
    def test_picks_cheapest_box_that_fits(self):
        rec = recommend_box([(BOOK, 1)], BOXES)
        self.assertEqual(rec.box.name, "Small")

    def test_quantity_pushes_to_bigger_box(self):
        rec = recommend_box([(BOOK, 10)], BOXES)  # 10 books cannot fit in Small
        self.assertEqual(rec.box.name, "Medium")

    def test_weight_limit_is_enforced(self):
        heavy = Item("ANVIL", 10, 10, 5, 3.0)  # fits Small by size, not by weight (2kg)
        rec = recommend_box([(heavy, 1)], BOXES)
        self.assertEqual(rec.box.name, "Medium")
        small_eval = next(e for e in rec.evaluations if e.box.name == "Small")
        self.assertIn("weight", small_eval.reason)

    def test_rotation_is_allowed(self):
        tall = Item("TALL", 5, 5, 24, 0.1)  # only fits Small when laid down
        rec = recommend_box([(tall, 1)], [SMALL])
        self.assertEqual(rec.box.name, "Small")

    def test_no_box_fits(self):
        rec = recommend_box([(TV, 1)], BOXES)
        self.assertIsNone(rec.box)
        self.assertIn("split", rec.message)

    def test_item_too_long_in_every_orientation(self):
        rod = Item("ROD", 100, 1, 1, 0.1)
        self.assertFalse(evaluate_box([rod], LARGE).fits)

    def test_exact_fit_boundary(self):
        exact = Item("EXACT", 25, 20, 10, 2.0)  # equals Small in size and weight
        self.assertTrue(evaluate_box([exact], SMALL).fits)

    def test_just_over_boundary_fails(self):
        over = Item("OVER", 25.01, 20, 10, 1.0)
        self.assertFalse(evaluate_box([over], SMALL).fits)

    def test_tie_on_cost_prefers_smaller_volume(self):
        a = BoxSpec("A", 30, 30, 30, 10, 3.0)
        b = BoxSpec("B", 20, 20, 20, 10, 3.0)
        rec = recommend_box([(MUG, 1)], [a, b])
        self.assertEqual(rec.box.name, "B")

    def test_cheaper_bigger_box_beats_pricier_smaller_box(self):
        pricey_small = BoxSpec("PS", 20, 20, 20, 10, 9.0)
        cheap_big = BoxSpec("CB", 50, 50, 50, 10, 1.0)
        rec = recommend_box([(MUG, 1)], [pricey_small, cheap_big])
        self.assertEqual(rec.box.name, "CB")

    def test_mixed_items(self):
        rec = recommend_box([(BOOK, 2), (MUG, 1)], BOXES)
        self.assertIsNotNone(rec.box)
        self.assertEqual(len(rec.placements), 3)

    def test_empty_order_rejected(self):
        with self.assertRaises(InvalidOrderError):
            recommend_box([], BOXES)

    def test_zero_quantity_rejected(self):
        with self.assertRaises(InvalidOrderError):
            recommend_box([(BOOK, 0)], BOXES)

    def test_bad_item_dimensions_rejected(self):
        with self.assertRaises(InvalidOrderError):
            recommend_box([(Item("BAD", 0, 1, 1, 1), 1)], BOXES)

    def test_volume_precheck_catches_impossible_load(self):
        # 9 mugs = 9000 cm^3 > Small (5000) volume
        self.assertFalse(evaluate_box([MUG] * 9, SMALL).fits)


class PackingCorrectnessTests(SimpleTestCase):
    def test_returned_placements_are_valid(self):
        rec = recommend_box([(BOOK, 6), (MUG, 3)], BOXES)
        self.assertTrue(verify_placements(rec.placements, rec.box.dims))

    def test_perfect_tiling_of_cubes(self):
        cube = Item("C", 10, 10, 10, 0.1)
        box = BoxSpec("Cube", 20, 20, 20, 10, 1)
        ev = evaluate_box([cube] * 8, box)  # 8 cubes fill 2x2x2 exactly
        self.assertTrue(ev.fits)
        self.assertTrue(verify_placements(ev.placements, box.dims))

    def test_nine_cubes_do_not_fit_2x2x2(self):
        cube = Item("C", 10, 10, 10, 0.1)
        box = BoxSpec("Cube", 20, 20, 20, 10, 1)
        self.assertFalse(evaluate_box([cube] * 9, box).fits)

    def test_verifier_detects_overlap(self):
        bad = [Placement("A", (0, 0, 0), (5, 5, 5)), Placement("B", (4, 4, 4), (5, 5, 5))]
        self.assertFalse(verify_placements(bad, (20, 20, 20)))

    def test_verifier_detects_out_of_bounds(self):
        bad = [Placement("A", (18, 0, 0), (5, 5, 5))]
        self.assertFalse(verify_placements(bad, (20, 20, 20)))

    def test_verifier_allows_touching_faces(self):
        ok = [Placement("A", (0, 0, 0), (5, 5, 5)), Placement("B", (5, 0, 0), (5, 5, 5))]
        self.assertTrue(verify_placements(ok, (20, 20, 20)))
