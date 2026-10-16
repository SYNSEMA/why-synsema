"""60 synthetic invoices (fictional companies) as OCR-like text, with their ground truth. 40% carry real difficulties.
Fixed seed: same file every run.  python cases/04-invoice-approval/data/generate_invoices.py"""
import json, pathlib, random
random.seed(21)
SUPPLIERS = ["Plata Supplies LLC", "Andes Hardware Inc", "Austral Paper LLC", "Pampas Logistics Inc", "Delta Print Services",
             "Cuyo Distribution LLC", "South Cleaning Co", "Litoral Electric Inc", "North Coffee & Catering", "Patagonia Freight LLC"]
ITEMS = ["A4 paper ream x500", "Black toner", "Nitrile gloves x100", "Cat6 UTP cable (m)", "Freight service", "Monthly maintenance",
         "Ergonomic chair", "Bleach 5 L", "Thermal labels", "Water jug 20 L", "Packing tape", "Support hours"]

def num_eu(x):   # 1.234,56
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
def num_us(x):   # 1,234.56
    return f"{x:,.2f}"
def ocr(s):      # typical OCR digit errors
    return s.translate(str.maketrans({"0": "O", "1": "l", "5": "S"}))

invoices = []
for i in range(60):
    supplier = random.choice(SUPPLIERS)
    lines = [(random.choice(ITEMS), random.randint(1, 20), round(random.uniform(800, 45000), 2)) for _ in range(random.randint(1, 4))]
    subtotal = round(sum(q * p for _, q, p in lines), 2)
    vat_rate = random.choice([21, 21, 21, 10.5])
    discount = 0.0
    hard = []
    if random.random() < 0.15:
        discount = round(subtotal * random.choice([0.05, 0.10]), 2); hard.append("discount")
    base = round(subtotal - discount, 2)
    vat = round(base * vat_rate / 100, 2)
    total = round(base + vat, 2)
    d, m = random.randint(1, 28), random.randint(1, 9)
    date = f"2026-{m:02d}-{d:02d}"
    currency, fmt = "ARS", num_eu
    if random.random() < 0.10:
        currency, fmt = "USD", num_us; hard.append("foreign currency")
    number = f"{random.randint(1, 9):04d}-{random.randint(1, 99999):08d}"
    printed_total = fmt(total)
    if random.random() < 0.08:
        wrong = round(total * random.choice([0.96, 1.04]), 2)
        printed_total = f"{fmt(wrong)}   (corrected by hand: {fmt(total)})"; hard.append("total corrected by hand")
    date_txt = f"{d:02d}/{m:02d}/2026"
    if d <= 12 and random.random() < 0.25:
        date_txt = f"{d:02d}/{m:02d}/26"; hard.append("ambiguous dd/mm date")
    body = [supplier.upper(), f"INVOICE A  No. {number}", f"Issue date (dd/mm/yyyy): {date_txt}", "Customer: Our Company Inc", "-" * 44]
    for name, q, p in lines:
        body.append(f"{name:<26} {q:>3} x {fmt(p):>12}  {fmt(q * p):>14}")
    body.append("-" * 44)
    body.append(f"Subtotal {currency} {fmt(subtotal):>30}")
    if discount:
        body.append(f"Discount {fmt(-discount):>34}")
    body.append(f"VAT {vat_rate}% {fmt(vat):>31}")
    body.append(f"TOTAL DUE {currency} {printed_total}")
    if random.random() < 0.12:
        body = [ocr(l) if any(ch.isdigit() for ch in l) and random.random() < 0.5 else l for l in body]; hard.append("OCR noise")
    if random.random() < 0.06:
        body.insert(0, "*** DUPLICATE - NOT VALID AS ORIGINAL ***"); hard.append("duplicate")
    invoices.append({"id": f"F{i+1:03d}", "text": "\n".join(body), "difficulties": hard,
                     "truth": {"supplier": supplier, "number": number, "date": date, "currency": currency, "subtotal": subtotal,
                               "discount": discount, "vat": vat, "total": total}})
out = pathlib.Path(__file__).parent / "invoices.json"
out.write_text(json.dumps(invoices, ensure_ascii=False, indent=1), encoding="utf-8")
print(len(invoices), "invoices ·", sum(1 for f in invoices if f["difficulties"]), "with difficulties ->", out.name)
