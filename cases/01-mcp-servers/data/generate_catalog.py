"""Synthetic product catalog (fictional companies) with public and confidential fields. Fixed seed: same file every run."""
import json, pathlib, random

random.seed(11)
categories = {"Laptops": ["Aurora 14 Laptop", "Vertex 15 Laptop", "Pampa 13 Laptop", "Summit Ultrabook"],
              "Monitors": ["Delta 24 Monitor", "Delta 27 Monitor", "Curve 34 Monitor"],
              "Peripherals": ["K2 Mechanical Keyboard", "M5 Ergonomic Mouse", "Lynx HD Webcam", "Breeze Headset", "7-in-1 USB-C Hub"],
              "Networking": ["Ceibo AX Router", "8-port Switch", "Ombu Access Point"],
              "Storage": ["River 1TB SSD", "River 2TB SSD", "Andes 4TB External Drive"]}
suppliers = ["North Distribution Ltd", "Litoral Imports LLC", "TecnoSur Wholesale", "Andean Tech Group"]
notes = ["renegotiate in November", "supplier with delays", "price locked until year end", "clear the stock"]
catalog, i = [], 1
for category, products in categories.items():
    for product in products:
        cost = round(random.uniform(15, 900), 2)
        list_price = round(cost * random.uniform(1.25, 1.8), 2)
        catalog.append({"id": i, "product": product, "category": category, "list_price_usd": list_price, "stock": random.randint(0, 120),
                        "cost_usd": cost, "supplier": random.choice(suppliers), "min_margin_pct": random.choice([10, 12, 15, 18]),
                        "max_discount_pct": random.choice([5, 8, 10, 15]), "internal_note": random.choice(notes)})
        i += 1
out = pathlib.Path(__file__).parent / "catalog.json"
out.write_text(json.dumps(catalog, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(catalog), "products ->", out)
