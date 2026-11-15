"""GPM IMERG daily precipitation totals over an AOI, via NASA Earthdata (earthaccess).

Uses the IMERG V07 daily product. Late Run (GPM_3IMERGDL) is the default because the
Final Run lags by months; Late Run is less bias-corrected. Requires Earthdata Login
(~/.netrc or EARTHDATA_USERNAME/EARTHDATA_PASSWORD).
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np

DEFAULT_SHORT_NAME = "GPM_3IMERGDL"
VERSION = "07"


def aoi_mean_mm(h5file, bbox: tuple[float, float, float, float]) -> float | None:
    """Area-mean daily precipitation (mm) from one IMERG daily file.

    Layout: Grid/precipitation (time, lon, lat) in mm/day, with Grid/lon and Grid/lat
    cell centres at 0.1 degree. Negative values are fill.
    """
    import h5py

    w, s, e, n = bbox
    with h5py.File(h5file, "r") as f:
        g = f["Grid"] if "Grid" in f else f
        lon, lat = g["lon"][:], g["lat"][:]
        xi = np.where((lon >= w - 0.05) & (lon <= e + 0.05))[0]
        yi = np.where((lat >= s - 0.05) & (lat <= n + 0.05))[0]
        if xi.size == 0 or yi.size == 0:
            return None
        p = g["precipitation"][0, xi.min(): xi.max() + 1, yi.min(): yi.max() + 1].astype("float64")
    p[p < 0] = np.nan
    return None if np.all(np.isnan(p)) else float(np.nanmean(p))


def accumulate(daily_mm: dict[date, float | None], start: date, end: date) -> tuple[float | None, int, int]:
    """Sum over days in [start, end). Returns (total_mm, days_with_data, days_expected)."""
    days = [start + timedelta(d) for d in range((end - start).days)]
    vals = [daily_mm.get(d) for d in days]
    have = [v for v in vals if v is not None]
    return (round(sum(have), 1) if have else None), len(have), len(days)


def fetch_daily(bbox, start: date, end: date, short_name: str = DEFAULT_SHORT_NAME) -> dict[date, float | None]:
    import earthaccess

    earthaccess.login(strategy="environment" if _env_creds() else "netrc")
    results = earthaccess.search_data(
        short_name=short_name, version=VERSION,
        temporal=(start.isoformat(), (end - timedelta(days=1)).isoformat()),
        bounding_box=tuple(bbox),
    )
    out: dict[date, float | None] = {}
    for granule, fh in zip(results, earthaccess.open(results)):
        begin = granule["umm"]["TemporalExtent"]["RangeDateTime"]["BeginningDateTime"][:10]
        out[date.fromisoformat(begin)] = aoi_mean_mm(fh, bbox)
    return out


def _env_creds() -> bool:
    import os

    return bool(os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD"))
