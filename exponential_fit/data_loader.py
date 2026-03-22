"""
Data loading from remote URLs (Excel Online, Google Sheets, direct links).
"""
import io
import re
from urllib.parse import urlparse, urlencode, parse_qs, urlunparse


def _make_download_url(url):
    """
    Convert an Excel Online / Google Sheets sharing URL to a direct download URL.

    Handles:
      - Google Sheets  → CSV export endpoint
      - OneDrive personal / SharePoint / 1drv.ms  → adds ``download=1``
      - Direct file URLs (.xlsx, .csv, …)  → returned unchanged
    """
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()

    # Google Sheets: extract sheet ID and convert to CSV export link
    # Match exact domain or www subdomain only
    if netloc in ("docs.google.com", "www.docs.google.com"):
        m = re.search(r"/spreadsheets/d/([^/]+)", parsed.path)
        if m:
            sheet_id = m.group(1)
            gid_m = re.search(r"gid=(\d+)", url)
            gid_part = f"&gid={gid_m.group(1)}" if gid_m else ""
            return (
                f"https://docs.google.com/spreadsheets/d/{sheet_id}"
                f"/export?format=csv{gid_part}"
            )

    # OneDrive (consumer) / SharePoint (business) / short 1drv.ms links
    # Use exact match or proper suffix check to avoid substring spoofing
    _onedrive_hosts = {"onedrive.live.com", "1drv.ms"}
    is_onedrive = netloc in _onedrive_hosts
    is_sharepoint = netloc == "sharepoint.com" or netloc.endswith(".sharepoint.com")
    if is_onedrive or is_sharepoint:
        qs = parse_qs(parsed.query, keep_blank_values=True)
        qs["download"] = ["1"]
        return urlunparse(parsed._replace(query=urlencode(qs, doseq=True)))

    return url


def load_data_from_url(url, x_col=0, y_col=1, sheet_name=0):
    """
    Download x/y data from a URL.

    Supported sources
    -----------------
    • Excel Online (OneDrive / SharePoint) share link — publicly shared files
    • Google Sheets share link — must be shared as "Anyone with link can view"
    • Any direct URL ending in .xlsx, .xls, or .csv

    The first column (``x_col=0``) is used as x-axis data and the second
    column (``y_col=1``) is used as y-axis data.

    Parameters
    ----------
    url : str
        URL to the data source.
    x_col : int
        Zero-based column index for x data (default: 0).
    y_col : int
        Zero-based column index for y data (default: 1).
    sheet_name : int or str
        Sheet to read for Excel files (default: 0, first sheet).

    Returns
    -------
    x : numpy.ndarray
    y : numpy.ndarray
    """
    try:
        import requests
    except ImportError as exc:
        raise ImportError("Please install 'requests': pip install requests") from exc
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError(
            "Please install 'pandas' and 'openpyxl': pip install pandas openpyxl"
        ) from exc

    if not url.startswith(("http://", "https://")):
        raise ValueError("URL must start with http:// or https://")

    download_url = _make_download_url(url)
    print(f"  Fetching: {download_url}")

    headers = {"User-Agent": "Mozilla/5.0 (compatible; ExponentialFit/2.0)"}
    resp = requests.get(download_url, headers=headers, timeout=60, allow_redirects=True)
    resp.raise_for_status()

    content_type = resp.headers.get("Content-Type", "")
    raw = io.BytesIO(resp.content)

    if "csv" in content_type or download_url.lower().endswith(".csv"):
        df = pd.read_csv(raw)
    elif download_url.lower().endswith(".xls"):
        df = pd.read_excel(raw, sheet_name=sheet_name, engine="xlrd")
    else:
        # Default: try Excel (xlsx); fall back to CSV if that fails
        try:
            df = pd.read_excel(raw, sheet_name=sheet_name, engine="openpyxl")
        except Exception:
            raw.seek(0)
            df = pd.read_csv(raw)

    x = pd.to_numeric(df.iloc[:, x_col], errors="coerce")
    y = pd.to_numeric(df.iloc[:, y_col], errors="coerce")
    # Drop rows where either column is NaN so x and y stay aligned
    valid = x.notna() & y.notna()
    return x[valid].values.astype(float), y[valid].values.astype(float)
