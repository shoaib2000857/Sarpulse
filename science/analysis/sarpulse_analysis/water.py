"""Open-water detection on L-band HH backscatter (dB).

Baseline: split-based Otsu thresholding. The image is cut into tiles; only tiles
with a clearly bimodal histogram (Ashman's D > 2 on a fitted two-Gaussian mixture,
smaller component >= 10 %) are pooled to pick the threshold, which keeps the threshold
from being dominated by land.
Threshold uncertainty is estimated by bootstrapping over the selected tiles.

References: Otsu (1979); Martinis et al. (2009) split-based thresholding;
Chini et al. (2017) hierarchical split-based approach and Ashman's D bimodality test.
"""

from dataclasses import asdict, dataclass, field

import numpy as np

MIN_ASHMAN_D = 2.0
MIN_CLASS_FRACTION = 0.1
MIN_TILES = 5


def _otsu_from_hist(hist: np.ndarray, edges: np.ndarray) -> float:
    centres = (edges[:-1] + edges[1:]) / 2
    w0 = np.cumsum(hist, dtype=np.float64)
    w1 = w0[-1] - w0
    m0 = np.cumsum(hist * centres)
    with np.errstate(divide="ignore", invalid="ignore"):
        mu0 = m0 / w0
        mu1 = (m0[-1] - m0) / w1
        between = w0 * w1 * (mu0 - mu1) ** 2
    between = np.nan_to_num(between, nan=-1.0)
    return float(edges[1:][np.argmax(between)])


def _range(v: np.ndarray) -> tuple[float, float]:
    lo, hi = np.percentile(v, [0.5, 99.5])
    return float(lo), float(hi if hi > lo else lo + 1e-3)


def otsu_threshold(values: np.ndarray, bins: int = 256) -> float:
    """Otsu's threshold over values between their 0.5th and 99.5th percentiles."""
    v = values[np.isfinite(values)]
    if v.size < 2:
        raise ValueError("Not enough values for Otsu")
    hist, edges = np.histogram(v, bins=bins, range=_range(v))
    return _otsu_from_hist(hist, edges)


def fit_two_gaussians(values: np.ndarray, iters: int = 50, max_n: int = 200_000, seed: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """1-D two-component Gaussian mixture by EM, initialised from a median split. Returns (weights, means, stds)."""
    v = values[np.isfinite(values)].astype(np.float64)
    if v.size > max_n:
        v = np.random.default_rng(seed).choice(v, max_n, replace=False)
    t = np.median(v)
    parts = [v[v < t], v[v >= t]]
    if min(p.size for p in parts) < 2:
        return np.array([1.0, 0.0]), np.array([v.mean(), v.mean()]), np.array([v.std(), v.std()])
    w = np.array([p.size for p in parts], dtype=np.float64) / v.size
    mu = np.array([p.mean() for p in parts])
    sd = np.array([p.std() for p in parts]) + 0.05
    for _ in range(iters):
        pdf = w / sd * np.exp(-0.5 * ((v[:, None] - mu) / sd) ** 2)
        resp = pdf / np.maximum(pdf.sum(axis=1, keepdims=True), 1e-300)
        n = resp.sum(axis=0) + 1e-12
        w = n / v.size
        mu = (resp * v[:, None]).sum(axis=0) / n
        sd = np.sqrt((resp * (v[:, None] - mu) ** 2).sum(axis=0) / n) + 0.05
    return w, mu, sd


def split_stats(values: np.ndarray) -> tuple[float, float]:
    """(Ashman's D, smaller mixture weight) from a fitted two-Gaussian mixture.

    D > 2 indicates a clean separation of two modes. D must come from fitted
    components: a hard split of a unimodal Gaussian would still give D ~ 2.7.
    """
    w, mu, sd = fit_two_gaussians(values)
    if w.min() < 1e-3:
        return 0.0, float(w.min())
    d = np.sqrt(2.0) * abs(mu[1] - mu[0]) / np.sqrt(sd[0] ** 2 + sd[1] ** 2)
    return float(d), float(w.min())


@dataclass
class ThresholdResult:
    threshold_db: float
    uncertainty_db: float  # half-width used for the ambiguous zone / area interval
    bootstrap_std_db: float
    method: str
    n_tiles_selected: int
    n_tiles_total: int
    ashman_d: float
    minor_class_fraction: float
    flags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        for k in ("threshold_db", "uncertainty_db", "bootstrap_std_db", "ashman_d", "minor_class_fraction"):
            d[k] = round(d[k], 3)
        return d


def _tiles(img: np.ndarray, size: int):
    h, w = img.shape
    for r in range(0, h - size + 1, size):
        for c in range(0, w - size + 1, size):
            yield img[r : r + size, c : c + size]


def split_based_threshold(
    db: np.ndarray,
    tile_px: int = 64,
    min_valid: float = 0.9,
    n_boot: int = 200,
    margin_db: float = 0.5,
    seed: int = 0,
) -> ThresholdResult:
    """Select a water/land threshold on a dB image (NaN = invalid)."""
    rng = np.random.default_rng(seed)
    candidates, total = [], 0
    for tile in _tiles(db, tile_px):
        finite = np.isfinite(tile)
        if finite.mean() < min_valid:
            continue
        total += 1
        v = tile[finite]
        d, frac = split_stats(v)
        if d > MIN_ASHMAN_D and frac >= MIN_CLASS_FRACTION:
            candidates.append(v)

    flags: list[str] = []
    bins = 256
    if len(candidates) >= MIN_TILES:
        # Bootstrap over tiles by resampling per-tile histograms on a common bin grid.
        sample = np.concatenate(candidates)
        edges = np.histogram_bin_edges(sample, bins=bins, range=_range(sample))
        hists = np.stack([np.histogram(v, bins=edges)[0] for v in candidates])
        threshold = _otsu_from_hist(hists.sum(axis=0), edges)
        idx = rng.integers(0, len(candidates), (n_boot, len(candidates)))
        boots = [_otsu_from_hist(hists[i].sum(axis=0), edges) for i in idx]
        method = f"split-based Otsu on {len(candidates)} bimodal {tile_px}px tiles (Ashman D>{MIN_ASHMAN_D})"
    else:
        sample = db[np.isfinite(db)]
        hist, edges = np.histogram(sample, bins=bins, range=_range(sample))
        threshold = _otsu_from_hist(hist, edges)
        n = int(hist.sum())
        boots = [_otsu_from_hist(rng.multinomial(n, hist / n), edges) for _ in range(n_boot)]
        method = "global Otsu fallback (too few bimodal tiles)"
        flags.append("global_otsu_fallback")

    d, frac = split_stats(sample)
    if d <= MIN_ASHMAN_D:
        flags.append("weak_bimodality")
    boot_std = float(np.std(boots))
    return ThresholdResult(
        threshold_db=threshold,
        uncertainty_db=max(1.96 * boot_std, margin_db),
        bootstrap_std_db=boot_std,
        method=method,
        n_tiles_selected=len(candidates),
        n_tiles_total=total,
        ashman_d=d,
        minor_class_fraction=frac,
        flags=flags,
    )


def gmm_water(hh_db: np.ndarray, hv_db: np.ndarray, max_samples: int = 200_000, seed: int = 0) -> np.ndarray:
    """Unsupervised 2-component Gaussian mixture on (HH, HV) dB; water = component with lower HH mean.

    Used only as an independent-method consistency check, not as accuracy evidence.
    """
    from sklearn.mixture import GaussianMixture

    ok = np.isfinite(hh_db) & np.isfinite(hv_db)
    X = np.column_stack([hh_db[ok], hv_db[ok]])
    rng = np.random.default_rng(seed)
    fit = X[rng.choice(len(X), min(len(X), max_samples), replace=False)]
    gm = GaussianMixture(n_components=2, covariance_type="full", random_state=seed).fit(fit)
    water_comp = int(np.argmin(gm.means_[:, 0]))
    out = np.zeros(hh_db.shape, dtype=bool)
    out[ok] = gm.predict(X) == water_comp
    return out


def agreement(a: np.ndarray, b: np.ndarray, valid: np.ndarray) -> dict:
    """Percent agreement and Cohen's kappa between two binary maps."""
    x, y = a[valid], b[valid]
    n = x.size
    if n == 0:
        return {"n_pixels": 0, "percent_agreement": None, "cohens_kappa": None}
    po = float(np.mean(x == y))
    pe = float(x.mean() * y.mean() + (1 - x.mean()) * (1 - y.mean()))
    kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
    return {"n_pixels": int(n), "percent_agreement": round(100 * po, 2), "cohens_kappa": round(kappa, 4)}
