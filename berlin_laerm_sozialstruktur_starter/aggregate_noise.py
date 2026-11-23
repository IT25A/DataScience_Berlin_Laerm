"""
Aggregiert echte Fassadenpegel des Berliner Lärm-WFS pro Planungsraum.

Dezibelwerte werden energetisch gemittelt:
10 * log10(mean(10^(dB/10)))
"""

import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import geopandas as gpd
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

WFS_URL = "https://gdi.berlin.de/services/wfs/ua_stratlaerm_2022"
TYPE_NAME = "ua_stratlaerm_2022:aa_fp_gesamt2022"
PAGE_SIZE = 100_000


def energetic_mean(values: pd.Series) -> float:
    values = pd.to_numeric(values, errors="coerce")
    values = values[(values > 0) & np.isfinite(values)]
    if values.empty:
        return np.nan
    return float(10.0 * np.log10(np.mean(np.power(10.0, values / 10.0))))


def fetch_page(start_index: int) -> dict:
    params = {
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetFeature",
        "typeNames": TYPE_NAME,
        "outputFormat": "application/json",
        "count": PAGE_SIZE,
        "startIndex": start_index,
    }
    url = f"{WFS_URL}?{urlencode(params)}"
    with urlopen(url, timeout=180) as response:
        return json.loads(response.read())


planning_areas = gpd.read_file(RAW / "planungsraeume.geojson")
if planning_areas.crs is None:
    raise ValueError("Planungsraum-Datei hat kein CRS.")

planning_areas = planning_areas.copy()
planning_areas["plr_id"] = (
    planning_areas["plr_id"].astype("string").str.strip().str.zfill(8)
)

PROCESSED.mkdir(parents=True, exist_ok=True)

first = fetch_page(0)
total = int(first.get("totalFeatures", first.get("numberMatched", 0)))
print(f"Fassadenpegel laut WFS: {total}")

all_rows = []
start_index = 0
while start_index < total:
    page = fetch_page(start_index) if start_index else first
    features = page.get("features", [])
    if not features:
        break

    rows = []
    x_coordinates = []
    y_coordinates = []
    for feature in features:
        coordinates = feature["geometry"]["coordinates"]
        rows.append(feature["properties"])
        x_coordinates.append(coordinates[0])
        y_coordinates.append(coordinates[1])

    page_df = pd.DataFrame(rows)
    required = {"ges_den", "ges_n", "str_den", "str_n"}
    missing = required.difference(page_df.columns)
    if missing:
        raise KeyError(f"Unerwartete WFS-Felder: {sorted(missing)}")

    points = gpd.GeoDataFrame(
        page_df,
        geometry=gpd.points_from_xy(x_coordinates, y_coordinates),
        crs="EPSG:25833",
    )
    joined = gpd.sjoin(
        points,
        planning_areas[["plr_id", "plr_name", "geometry"]],
        how="inner",
        predicate="within",
    )
    all_rows.append(joined)

    start_index += len(features)
    print(f"Verarbeitet: {start_index}/{total}")

if not all_rows:
    raise RuntimeError("Kein Fassadenpegel konnte den Planungsraeumen zugeordnet werden.")

points_in_plr = pd.concat(all_rows, ignore_index=True)

aggregation = (
    points_in_plr.groupby("plr_id", as_index=False)
    .agg(
        anzahl_laermpegel=("importid", "count"),
        anzahl_gesamtlaerm_lden=("ges_den", "count"),
        anzahl_gesamtlaerm_ln=("ges_n", "count"),
        anzahl_strassenlaerm_lden=("str_den", "count"),
        anzahl_strassenlaerm_ln=("str_n", "count"),
    )
)

energetic_columns = {
    "laerm_gesamt_lden_db": "ges_den",
    "laerm_gesamt_ln_db": "ges_n",
    "laerm_strassen_lden_db": "str_den",
    "laerm_strassen_ln_db": "str_n",
}
for output_column, source_column in energetic_columns.items():
    energy = (
        points_in_plr.groupby("plr_id")[source_column]
        .apply(energetic_mean)
        .rename(output_column)
    )
    aggregation = aggregation.merge(energy, on="plr_id", how="left")

result = planning_areas[["plr_id", "plr_name"]].merge(
    aggregation,
    on="plr_id",
    how="left",
)

output_csv = PROCESSED / "laermdaten_aggregiert.csv"
result.to_csv(output_csv, index=False)

output_geojson = PROCESSED / "laermdaten_aggregiert.geojson"
result_gdf = planning_areas.merge(
    result.drop(columns="plr_name"),
    on="plr_id",
    how="left",
)
result_gdf.to_file(output_geojson, driver="GeoJSON")

print(f"\nLärmdaten gespeichert: {output_csv}")
print(f"PLR mit Gesamt-LDEN: {result['laerm_gesamt_lden_db'].notna().sum()}/{len(result)}")
print(result[
    ["laerm_gesamt_lden_db", "laerm_gesamt_ln_db", "laerm_strassen_lden_db", "laerm_strassen_ln_db"]
].describe().round(2).to_string())
