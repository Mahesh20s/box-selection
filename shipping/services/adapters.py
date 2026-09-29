"""Convert Django model instances to the pure dataclasses used by the packer."""
from .packing import BoxSpec, Item


def product_to_item(product) -> Item:
    return Item(product.sku, float(product.length), float(product.width), float(product.height), float(product.weight))


def box_to_spec(box) -> BoxSpec:
    return BoxSpec(box.name, float(box.length), float(box.width), float(box.height), float(box.max_weight), float(box.cost))
