"""Correct answers, computed by hand with polars, used to grade the three variants. Run from the repository root:
    uv run --with polars python cases/02-llm-written-analytics/comparison/truth.py"""
import json, pathlib, polars as pl
D = "cases/02-llm-written-analytics/data/"
v = {}
b = pl.read_csv(D + "books.csv")
g = b.group_by("category").agg(pl.len().alias("n"), pl.col("price").mean().alias("p")).filter(pl.col("n") >= 5).sort("p", descending=True).row(0, named=True)
v[1] = f"{g['category']}: {g['n']} books, mean price {g['p']:.2f}"
c = pl.read_csv(D + "weather_summary.csv").sort("rain_total_mm", descending=True).head(3)
v[2] = "; ".join(f"{r['city']} {r['rain_total_mm']:.0f} mm, {r['temp_mean']:.1f} °C" for r in c.iter_rows(named=True))
p = pl.read_csv(D + "steam_regional_prices.csv").group_by("country").agg(pl.col("index").median()).sort("index").row(0, named=True)
v[3] = f"{p['country']}: {p['index']:.1f}"
s = pl.read_csv(D + "game_prices.csv").group_by("cheapest_store").agg(pl.len().alias("n"), pl.col("discount_pct").mean().alias("d")).sort("n", descending=True).row(0, named=True)
v[4] = f"{s['cheapest_store']}: {s['n']} games, mean discount {s['d']:.1f}%"
hb = pl.read_parquet(D + "taxi_hour_borough.parquet").filter(pl.col("borough") == "Brooklyn").sort("mph").row(0, named=True)
v[5] = f"{hb['hour']}h: {hb['mph']:.2f} mph, tip {hb['tip_pct']:.2f}%"
od = pl.read_parquet(D + "taxi_top_routes.parquet").filter(~pl.col("origin").str.contains("Upper East Side") & ~pl.col("destination").str.contains("Upper East Side")).sort("trips", descending=True).row(0, named=True)
v[6] = f"{od['origin']} -> {od['destination']}: {od['trips']} trips"
m = pl.read_parquet(D + "taxi_monthly.parquet").with_columns((pl.col("revenue") / pl.col("trips")).alias("x")).sort("x", descending=True).row(0, named=True)
v[7] = f"{m['month']}: {m['x']:.2f} USD per trip"
dv = pl.read_csv(D + "demand_validation.csv").with_columns(((pl.col("model") - pl.col("actual")).abs() / pl.col("actual")).alias("e"))
v[8] = f"{dv.filter(pl.col('e') > 0.10).height} days; worst {dv.sort('e', descending=True).row(0, named=True)['date']} ({dv['e'].max()*100:.1f}%)"
tr = pl.read_ndjson(D + "trades.jsonl").filter(pl.col("pair") == "BTC").group_by("exchange").agg(((pl.col("price") * pl.col("size")).sum() / pl.col("size").sum()).alias("vwap"))
w = {r["exchange"]: r["vwap"] for r in tr.iter_rows(named=True)}
v[9] = f"binance {w['binance']:.2f}, coinbase {w['coinbase']:.2f}, difference {(w['coinbase']/w['binance']-1)*10000:.1f} bps"
e = pl.read_csv(D + "teacher_labels.csv").with_columns((pl.col("teacher") == pl.col("truth")).alias("ok")).group_by("source").agg(pl.len().alias("n"), (pl.col("ok").mean() * 100).alias("pct")).sort("source")
v[10] = "; ".join(f"{r['source']} {r['pct']:.1f}% (n={r['n']})" for r in e.iter_rows(named=True))
pathlib.Path("cases/02-llm-written-analytics/comparison/truth.json").write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
for k, x in v.items(): print(k, x)
