#!/usr/bin/env python3
"""Download and deterministically convert the 12 new tables from UCI archives."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent
CACHE = Path(os.environ.get("MLCA_BENCHMARK_CACHE", tempfile.gettempdir())) / "mlca-uci-cache"

DATASETS = [
    ("datasets/covertype_uci.csv", 31, "covertype", "covtype.data.gz", "header"),
    ("datasets/anuran_calls_uci.csv", 406, "anuran+calls+mfccs", "Frogs_MFCCs.csv", "csv"),
    ("datasets/abalone_uci.csv", 1, "abalone", "abalone.data", "header"),
    ("datasets/bike_sharing_hourly_uci.csv", 275, "bike+sharing+dataset", "hour.csv", "csv"),
    ("datasets/energy_efficiency_uci.csv", 242, "energy+efficiency", "ENB2012_data.xlsx", "excel_energy"),
    ("datasets/seeds_uci.csv", 236, "seeds", "seeds_dataset.txt", "seeds"),
    ("datasets/online_retail_uci.csv", 352, "online+retail", "Online Retail.xlsx", "excel_retail"),
    ("datasets/optical_digits_uci.csv", 80, "optical+recognition+of+handwritten+digits", "optdigits", "digits"),
    ("heldout/bank_marketing_uci.csv", 222, "bank+marketing", "bank.zip", "bank"),
    ("heldout/steel_plates_faults_uci.csv", 198, "steel+plates+faults", "Faults.NNA", "steel"),
    ("heldout/wine_quality_uci.csv", 186, "wine+quality", "wine", "wine"),
    ("heldout/wholesale_customers_uci.csv", 292, "wholesale+customers", "Wholesale customers data.csv", "csv"),
]

SEED_HEADER = ["area", "perimeter", "compactness", "kernel_length", "kernel_width", "asymmetry_coefficient", "groove_length", "variety"]
COOVER_HEADER = ["Elevation", "Aspect", "Slope", "Horizontal_Distance_To_Hydrology", "Vertical_Distance_To_Hydrology", "Horizontal_Distance_To_Roadways", "Hillshade_9am", "Hillshade_Noon", "Hillshade_3pm", "Horizontal_Distance_To_Fire_Points"] + [f"Wilderness_Area{i}" for i in range(1, 5)] + [f"Soil_Type{i}" for i in range(1, 41)] + ["Cover_Type"]
STEEL_HEADER = "X_Minimum X_Maximum Y_Minimum Y_Maximum Pixels_Areas X_Perimeter Y_Perimeter Sum_of_Luminosity Minimum_of_Luminosity Maximum_of_Luminosity Length_of_Conveyer TypeOfSteel_A300 TypeOfSteel_A400 Steel_Plate_Thickness Edges_Index Empty_Index Square_Index Outside_X_Index Edges_X_Index Edges_Y_Index Outside_Global_Index LogOfAreas Log_X_Index Log_Y_Index Orientation_Index Luminosity_Index SigmoidOfAreas Pastry Z_Scratch K_Scatch Stains Dirtiness Bumps Other_Faults".split()


def download(url: str, path: Path) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": "mlca-benchmark-preparation/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, path.open("wb") as output:
        shutil.copyfileobj(response, output)


def archive_member(dataset_id: int, slug: str, filename: str) -> bytes:
    archive = CACHE / f"{dataset_id}.zip"
    download(f"https://archive.ics.uci.edu/static/public/{dataset_id}/{slug}.zip", archive)
    with zipfile.ZipFile(archive) as zf:
        matches = [name for name in zf.namelist() if Path(name).name.casefold() == filename.casefold()]
        if not matches:
            raise FileNotFoundError(f"{filename!r} not found in official UCI archive {dataset_id}")
        payload = zf.read(matches[0])
    return gzip.decompress(payload) if filename.endswith(".gz") else payload


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, lineterminator="\n", encoding="utf-8", na_rep="")


def convert(dataset_id: int, slug: str, filename: str, kind: str, destination: Path) -> None:
    if kind == "digits":
        train = archive_member(dataset_id, slug, "optdigits.tra")
        test = archive_member(dataset_id, slug, "optdigits.tes")
        header = [f"pixel_{i}" for i in range(1, 65)] + ["digit"]
        frames = [pd.read_csv(io.BytesIO(data), header=None) for data in (train, test)]
        write_csv(destination, pd.concat(frames, ignore_index=True).set_axis(header, axis=1))
    elif kind == "bank":
        payload = archive_member(dataset_id, slug, filename)
        with zipfile.ZipFile(io.BytesIO(payload)) as inner:
            csv_data = next(inner.read(n) for n in inner.namelist() if Path(n).name == "bank-full.csv")
        write_csv(destination, pd.read_csv(io.BytesIO(csv_data), sep=";", dtype=str, keep_default_na=False))
    elif kind == "wine":
        frames = []
        for color in ("red", "white"):
            raw = archive_member(dataset_id, slug, f"winequality-{color}.csv")
            frame = pd.read_csv(io.BytesIO(raw), sep=";", dtype=str, keep_default_na=False)
            frame.insert(len(frame.columns) - 1, "color", color)
            frames.append(frame)
        write_csv(destination, pd.concat(frames, ignore_index=True))
    elif kind == "steel":
        payload = archive_member(dataset_id, slug, filename)
        frame = pd.read_csv(io.BytesIO(payload), sep=r"\s+", header=None, names=STEEL_HEADER, dtype=str)
        write_csv(destination, frame)
    elif kind == "header":
        payload = archive_member(dataset_id, slug, filename)
        header = COOVER_HEADER if dataset_id == 31 else ["Sex", "Length", "Diameter", "Height", "Whole_weight", "Shucked_weight", "Viscera_weight", "Shell_weight", "Rings"]
        frame = pd.read_csv(io.BytesIO(payload), header=None, names=header, dtype=str)
        write_csv(destination, frame)
    elif kind == "seeds":
        payload = archive_member(dataset_id, slug, filename)
        frame = pd.read_csv(io.BytesIO(payload), sep=r"\s+", header=None, names=SEED_HEADER, dtype=str)
        write_csv(destination, frame)
    elif kind == "excel_energy":
        payload = archive_member(dataset_id, slug, filename)
        frame = pd.read_excel(io.BytesIO(payload), dtype=str, engine="openpyxl")
        write_csv(destination, frame)
    elif kind == "excel_retail":
        payload = archive_member(dataset_id, slug, filename)
        frame = pd.read_excel(io.BytesIO(payload), dtype={"InvoiceNo": str, "StockCode": str, "CustomerID": str}, engine="openpyxl")
        frame["InvoiceDate"] = pd.to_datetime(frame["InvoiceDate"]).dt.strftime("%Y-%m-%dT%H:%M:%S")
        write_csv(destination, frame)
    else:
        payload = archive_member(dataset_id, slug, filename)
        frame = pd.read_csv(io.BytesIO(payload), dtype=str, keep_default_na=False)
        write_csv(destination, frame)


def main() -> None:
    global CACHE
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, default=CACHE, help="outside-repository download cache")
    args = parser.parse_args()
    CACHE = args.cache
    for relative, dataset_id, slug, filename, kind in DATASETS:
        destination = ROOT / relative
        convert(dataset_id, slug, filename, kind, destination)
        print(f"wrote {relative}")


if __name__ == "__main__":
    main()
