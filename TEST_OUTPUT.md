# Test output

Command: `python manage.py test -v 2` (Python 3.12, Django 6.1.1)

```
Found 33 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, sessions, shipping
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying sessions.0001_initial... OK
  Applying shipping.0001_initial... OK
System check identified no issues (0 silenced).
test_bad_quantity_400 (shipping.tests.test_api.ApiTests.test_bad_quantity_400) ... ok
test_empty_items_400 (shipping.tests.test_api.ApiTests.test_empty_items_400) ... ok
test_empty_saved_order_400 (shipping.tests.test_api.ApiTests.test_empty_saved_order_400) ... ok
test_get_not_allowed (shipping.tests.test_api.ApiTests.test_get_not_allowed) ... ok
test_inactive_boxes_are_ignored (shipping.tests.test_api.ApiTests.test_inactive_boxes_are_ignored) ... ok
test_invalid_json_400 (shipping.tests.test_api.ApiTests.test_invalid_json_400) ... ok
test_no_box_fits_returns_200_with_null_box (shipping.tests.test_api.ApiTests.test_no_box_fits_returns_200_with_null_box) ... ok
test_order_not_found (shipping.tests.test_api.ApiTests.test_order_not_found) ... ok
test_recommend_by_payload (shipping.tests.test_api.ApiTests.test_recommend_by_payload) ... ok
test_recommend_for_saved_order (shipping.tests.test_api.ApiTests.test_recommend_for_saved_order) ... ok
test_unknown_sku_404 (shipping.tests.test_api.ApiTests.test_unknown_sku_404) ... ok
test_root_lists_endpoints (shipping.tests.test_api.IndexTests.test_root_lists_endpoints) ... ok
test_nine_cubes_do_not_fit_2x2x2 (shipping.tests.test_packing.PackingCorrectnessTests.test_nine_cubes_do_not_fit_2x2x2) ... ok
test_perfect_tiling_of_cubes (shipping.tests.test_packing.PackingCorrectnessTests.test_perfect_tiling_of_cubes) ... ok
test_returned_placements_are_valid (shipping.tests.test_packing.PackingCorrectnessTests.test_returned_placements_are_valid) ... ok
test_verifier_allows_touching_faces (shipping.tests.test_packing.PackingCorrectnessTests.test_verifier_allows_touching_faces) ... ok
test_verifier_detects_out_of_bounds (shipping.tests.test_packing.PackingCorrectnessTests.test_verifier_detects_out_of_bounds) ... ok
test_verifier_detects_overlap (shipping.tests.test_packing.PackingCorrectnessTests.test_verifier_detects_overlap) ... ok
test_bad_item_dimensions_rejected (shipping.tests.test_packing.RecommendationTests.test_bad_item_dimensions_rejected) ... ok
test_cheaper_bigger_box_beats_pricier_smaller_box (shipping.tests.test_packing.RecommendationTests.test_cheaper_bigger_box_beats_pricier_smaller_box) ... ok
test_empty_order_rejected (shipping.tests.test_packing.RecommendationTests.test_empty_order_rejected) ... ok
test_exact_fit_boundary (shipping.tests.test_packing.RecommendationTests.test_exact_fit_boundary) ... ok
test_item_too_long_in_every_orientation (shipping.tests.test_packing.RecommendationTests.test_item_too_long_in_every_orientation) ... ok
test_just_over_boundary_fails (shipping.tests.test_packing.RecommendationTests.test_just_over_boundary_fails) ... ok
test_mixed_items (shipping.tests.test_packing.RecommendationTests.test_mixed_items) ... ok
test_no_box_fits (shipping.tests.test_packing.RecommendationTests.test_no_box_fits) ... ok
test_picks_cheapest_box_that_fits (shipping.tests.test_packing.RecommendationTests.test_picks_cheapest_box_that_fits) ... ok
test_quantity_pushes_to_bigger_box (shipping.tests.test_packing.RecommendationTests.test_quantity_pushes_to_bigger_box) ... ok
test_rotation_is_allowed (shipping.tests.test_packing.RecommendationTests.test_rotation_is_allowed) ... ok
test_tie_on_cost_prefers_smaller_volume (shipping.tests.test_packing.RecommendationTests.test_tie_on_cost_prefers_smaller_volume) ... ok
test_volume_precheck_catches_impossible_load (shipping.tests.test_packing.RecommendationTests.test_volume_precheck_catches_impossible_load) ... ok
test_weight_limit_is_enforced (shipping.tests.test_packing.RecommendationTests.test_weight_limit_is_enforced) ... ok
test_zero_quantity_rejected (shipping.tests.test_packing.RecommendationTests.test_zero_quantity_rejected) ... ok

----------------------------------------------------------------------
Ran 33 tests in 0.096s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...