"""Per-date water maps and before/after change classes with explicit ambiguity.

A pixel is only called `water_gained` / `water_lost` when (1) its water label differs
between the dates, (2) neither label lies inside the threshold-uncertainty band and
(3) HH backscatter changed by at least `min_change_db` in the expected direction.
Everything else that cannot be decided is `ambiguous`; nothing is silently forced.
"""

from dataclasses import dataclass, field

import numpy as np

from .features import lee_filter, to_db
from .water import ThresholdResult, agreement, gmm_water, split_based_threshold

CLASS_CODES = {"stable_land": 0, "water_gained": 1, "water_lost": 2, "stable_water": 3, "ambiguous": 4}
CLASS_NAMES = {v: k for k, v in CLASS_CODES.items()}
NODATA = 255
CLASS_DEFINITIONS = {
    "stable_land": "Not classified as open water on either date",
    "water_gained": "Land before, open water after, with HH decrease >= min_change_db",
    "water_lost": "Open water before, land after, with HH increase >= min_change_db",
    "stable_water": "Classified as open water on both dates",
    "ambiguous": "Water label within threshold uncertainty on either date, or label change without sufficient HH change",
}


@dataclass
class Params:
    speckle_filter: str = "lee"  # "lee" or "none"
    filter_size: int = 5
    tile_px: int = 64
    margin_db: float = 0.5
    min_change_db: float = 3.0
    n_boot: int = 200
    seed: int = 0
    gmm_check: bool = True

    def __post_init__(self):
        if self.speckle_filter not in ("lee", "none"):
            raise ValueError("speckle_filter must be lee or none")
        if self.filter_size < 1 or self.filter_size % 2 != 1 or self.tile_px < 2 or self.n_boot < 2:
            raise ValueError("filter_size must be positive and odd; tile_px and n_boot must be >= 2")
        if self.margin_db < 0 or self.min_change_db < 0:
            raise ValueError("margin_db and min_change_db must be nonnegative")

    def to_dict(self) -> dict:
        return dict(self.__dict__)


@dataclass
class DateResult:
    scene_id: str
    date: str
    hh_db: np.ndarray
    hv_db: np.ndarray
    valid: np.ndarray
    threshold: ThresholdResult
    water: np.ndarray
    uncertain: np.ndarray
    enl: float | None
    method_agreement: dict | None = None
    flags: list[str] = field(default_factory=list)


def classify_date(scene_id: str, date: str, hh: np.ndarray, hv: np.ndarray, valid: np.ndarray, p: Params) -> DateResult:
    """Water map for one acquisition from linear-power HH/HV."""
    enl = None
    if p.speckle_filter == "lee":
        hh, enl = lee_filter(hh, p.filter_size)
        hv, _ = lee_filter(hv, p.filter_size, enl)
    hh_db, hv_db = to_db(hh), to_db(hv)
    valid = valid & np.isfinite(hh_db) & np.isfinite(hv_db)
    hh_db[~valid] = np.nan
    hv_db[~valid] = np.nan

    thr = split_based_threshold(hh_db, tile_px=p.tile_px, n_boot=p.n_boot, margin_db=p.margin_db, seed=p.seed)
    water = valid & (hh_db < thr.threshold_db)
    uncertain = valid & (np.abs(hh_db - thr.threshold_db) < thr.uncertainty_db)
    result = DateResult(scene_id, date, hh_db, hv_db, valid, thr, water, uncertain, enl, flags=list(thr.flags))
    if p.gmm_check:
        result.method_agreement = agreement(water, gmm_water(hh_db, hv_db, seed=p.seed), valid)
    return result


def _raw_change(wb: np.ndarray, wa: np.ndarray, delta: np.ndarray, valid: np.ndarray, min_change_db: float):
    gained = valid & ~wb & wa & (delta <= -min_change_db)
    lost = valid & wb & ~wa & (delta >= min_change_db)
    return gained, lost


def change_map(before: DateResult, after: DateResult, p: Params) -> tuple[np.ndarray, dict]:
    """uint8 change classes (CLASS_CODES, NODATA outside common valid area) and area diagnostics."""
    valid = before.valid & after.valid
    wb, wa = before.water, after.water
    delta = after.hh_db - before.hh_db

    cls = np.full(valid.shape, NODATA, dtype=np.uint8)
    cls[valid & ~wb & ~wa] = CLASS_CODES["stable_land"]
    cls[valid & wb & wa] = CLASS_CODES["stable_water"]
    cls[valid & ~wb & wa] = CLASS_CODES["water_gained"]
    cls[valid & wb & ~wa] = CLASS_CODES["water_lost"]

    weak_gain = (cls == CLASS_CODES["water_gained"]) & ~(delta <= -p.min_change_db)
    weak_loss = (cls == CLASS_CODES["water_lost"]) & ~(delta >= p.min_change_db)
    ambiguous = valid & (before.uncertain | after.uncertain | weak_gain | weak_loss)
    cls[ambiguous] = CLASS_CODES["ambiguous"]

    # Sensitivity: change areas when each date's threshold moves within its uncertainty.
    gained_range, lost_range = [], []
    tb, ta = before.threshold, after.threshold
    for sb in (-1, 0, 1):
        for sa in (-1, 0, 1):
            wb_s = valid & (before.hh_db < tb.threshold_db + sb * tb.uncertainty_db)
            wa_s = valid & (after.hh_db < ta.threshold_db + sa * ta.uncertainty_db)
            g, lo = _raw_change(wb_s, wa_s, delta, valid, p.min_change_db)
            gained_range.append(int(g.sum()))
            lost_range.append(int(lo.sum()))

    brightening = valid & ~wb & ~wa & (delta >= p.min_change_db)
    diagnostics = {
        "valid_pixels": int(valid.sum()),
        "class_pixels": {name: int((cls == code).sum()) for name, code in CLASS_CODES.items()},
        "gained_pixels_range": [min(gained_range), max(gained_range)],
        "lost_pixels_range": [min(lost_range), max(lost_range)],
        "hh_brightening_non_water_pixels": int(brightening.sum()),
        "delta_hh_db": delta,
    }
    return cls, diagnostics
