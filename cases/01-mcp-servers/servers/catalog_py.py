"""Shared logic for both Python servers: load the catalog and compute quotes."""
import json, pathlib

CATALOG = json.loads((pathlib.Path(__file__).parent.parent / "data" / "catalog.json").read_text(encoding="utf-8"))
PUBLIC = ["id", "product", "category", "list_price_usd", "stock"]


def find(pid: int) -> dict:
    for p in CATALOG:
        if p["id"] == pid:
            return p
    raise ValueError(f"no product with id {pid}")


def public_view(p: dict) -> dict:
    return {k: p[k] for k in PUBLIC}


def quote(pid: int, quantity: int, discount_pct: float) -> dict:
    """Cost and margins are used in here; only the price leaves."""
    p = find(pid)
    discount = min(max(discount_pct, 0), p["max_discount_pct"])
    unit = p["list_price_usd"] * (1 - discount / 100)
    floor = p["cost_usd"] * (1 + p["min_margin_pct"] / 100)
    adjusted = unit < floor
    unit = round(max(unit, floor), 2)
    return {"product": p["product"], "quantity": quantity, "discount_applied_pct": discount if not adjusted else None,
            "unit_price_usd": unit, "total_usd": round(unit * quantity, 2), "raised_to_minimum": adjusted}
