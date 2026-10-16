"""Typical Python ETL: daily weather for 5 cities (last 30 days) -> Parquet + CSV summary."""
import datetime as dt, json, sys
import requests, pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv
import helpers

load_dotenv()
CITIES = {"Buenos Aires": (-34.61, -58.38), "Santiago": (-33.45, -70.67), "Lima": (-12.05, -77.04), "Bogotá": (4.71, -74.07), "Madrid": (40.42, -3.70)}

@retry(stop=stop_after_attempt(4), wait=wait_exponential(min=1, max=10))
def fetch(lat, lon, start, end):
    r = requests.get("https://archive-api.open-meteo.com/v1/archive", params={"latitude": lat, "longitude": lon, "start_date": start,
                     "end_date": end, "daily": "temperature_2m_max,precipitation_sum", "timezone": "auto"}, timeout=30)
    r.raise_for_status()
    return r.json()["daily"]

end = dt.date(2026, 10, 10); start = end - dt.timedelta(days=29)
rows = []
for city, (lat, lon) in CITIES.items():
    d = fetch(lat, lon, start.isoformat(), end.isoformat())
    rows += [{"city": city, "date": f, "tmax": t, "rain": p} for f, t, p in zip(d["time"], d["temperature_2m_max"], d["precipitation_sum"])]
df = pd.DataFrame(rows)
df.to_parquet(sys.argv[1] + "/weather_python.parquet", index=False)
summary = df.groupby("city").agg(tmax_mean=("tmax", "mean"), rain_total=("rain", "sum")).reset_index()
summary["tmax_mean"] = summary["tmax_mean"].map(helpers.round1)
summary.to_csv(sys.argv[1] + "/summary_python.csv", index=False)
print(summary.to_string(index=False))
print("what the imported module can do:", json.dumps(helpers.capabilities(), ensure_ascii=False))
