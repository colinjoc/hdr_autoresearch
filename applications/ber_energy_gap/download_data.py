"""Download SEAI BER Public Search dataset.

Downloads the full BER dataset from the SEAI National BER Research Tool.
The data is a tab-delimited text file containing ~1.4M domestic BER certificates.
"""
import os
import re
import requests
import zipfile
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ZIP_PATH = os.path.join(DATA_DIR, "BERPublicSearch.zip")
PARQUET_PATH = os.path.join(DATA_DIR, "ber_raw.parquet")

SEAI_URL = "https://ndber.seai.ie/BERResearchTool/ber/search.aspx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def download_ber_zip():
    """Download BER dataset ZIP from SEAI research tool."""
    if os.path.exists(ZIP_PATH):
        print(f"ZIP already exists: {ZIP_PATH}")
        return ZIP_PATH

    os.makedirs(DATA_DIR, exist_ok=True)
    session = requests.Session()

    # GET the page to extract ASP.NET form fields
    print("Fetching SEAI BER Research Tool page...")
    resp = session.get(SEAI_URL, headers=HEADERS)
    resp.raise_for_status()

    viewstate = re.search(r'id="__VIEWSTATE"\s+value="([^"]*)"', resp.text)
    viewstategen = re.search(r'id="__VIEWSTATEGENERATOR"\s+value="([^"]*)"', resp.text)
    eventvalidation = re.search(r'id="__EVENTVALIDATION"\s+value="([^"]*)"', resp.text)

    if not all([viewstate, viewstategen, eventvalidation]):
        raise RuntimeError("Could not extract ASP.NET form fields from SEAI page")

    # POST to trigger download
    data = {
        "__VIEWSTATE": viewstate.group(1),
        "__VIEWSTATEGENERATOR": viewstategen.group(1),
        "__EVENTVALIDATION": eventvalidation.group(1),
        "ctl00$DefaultContent$BERSearch$dfExcelDownlaod$DownloadAllData": "Download All Data",
    }

    print("Downloading full BER dataset (this may take several minutes)...")
    resp2 = session.post(SEAI_URL, data=data, headers=HEADERS, stream=True)
    resp2.raise_for_status()

    ct = resp2.headers.get("Content-Type", "")
    if "zip" not in ct and "octet" not in ct:
        raise RuntimeError(f"Unexpected content type: {ct}")

    with open(ZIP_PATH, "wb") as f:
        for chunk in resp2.iter_content(chunk_size=65536):
            f.write(chunk)

    size_mb = os.path.getsize(ZIP_PATH) / 1e6
    print(f"Downloaded {size_mb:.1f} MB to {ZIP_PATH}")
    return ZIP_PATH


def extract_to_parquet():
    """Extract BER data from ZIP and save as Parquet."""
    if os.path.exists(PARQUET_PATH):
        print(f"Parquet already exists: {PARQUET_PATH}")
        return PARQUET_PATH

    if not os.path.exists(ZIP_PATH):
        download_ber_zip()

    print("Extracting BER data from ZIP...")
    z = zipfile.ZipFile(ZIP_PATH)

    with z.open("BERPublicsearch.txt") as f:
        df = pd.read_csv(
            f, sep="\t", low_memory=False, encoding="latin-1", on_bad_lines="skip"
        )

    print(f"Loaded {len(df):,} records with {len(df.columns)} columns")

    # Strip whitespace from string columns
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].str.strip()

    df.to_parquet(PARQUET_PATH, index=False, engine="pyarrow")
    size_mb = os.path.getsize(PARQUET_PATH) / 1e6
    print(f"Saved {size_mb:.1f} MB to {PARQUET_PATH}")
    return PARQUET_PATH


if __name__ == "__main__":
    download_ber_zip()
    extract_to_parquet()
