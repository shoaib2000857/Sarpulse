"""Radar features: dB conversion, speckle filtering and polarization ratios.

All filtering is done on linear power (intensity), never on dB values.
"""

import numpy as np
from scipy.ndimage import uniform_filter


def to_db(power: np.ndarray) -> np.ndarray:
    with np.errstate(divide="ignore", invalid="ignore"):
        return (10.0 * np.log10(power)).astype(np.float32)


def _local_moments(img: np.ndarray, size: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """NaN-aware local mean, variance and valid fraction over a size x size window."""
    valid = np.isfinite(img)
    filled = np.where(valid, img, 0.0).astype(np.float64)
    w = uniform_filter(valid.astype(np.float64), size, mode="constant")
    s1 = uniform_filter(filled, size, mode="constant")
    s2 = uniform_filter(filled * filled, size, mode="constant")
    with np.errstate(divide="ignore", invalid="ignore"):
        mean = s1 / w
        var = np.maximum(s2 / w - mean * mean, 0.0)
    return mean, var, w


def estimate_enl(power: np.ndarray, size: int = 11) -> float:
    """Equivalent number of looks as 1 / mode of the local CV^2 (= var / mean^2) distribution.

    The mode is dominated by homogeneous areas and, unlike picking the lowest-variance
    windows, is not biased upward by windows that are smooth only by chance.
    """
    mean, var, w = _local_moments(power, size)
    ok = (w > 0.999) & (var > 0) & np.isfinite(mean) & (mean > 0)
    if ok.sum() < 100:
        return 1.0
    log_cv2 = np.log(var[ok] / mean[ok] ** 2)
    hist, edges = np.histogram(log_cv2, bins=100)
    i = int(np.argmax(hist))
    return float(1.0 / np.exp((edges[i] + edges[i + 1]) / 2))


def lee_filter(power: np.ndarray, size: int = 5, enl: float | None = None) -> tuple[np.ndarray, float]:
    """Classic Lee filter on intensity. Returns (filtered, enl used). NaNs stay NaN."""
    if enl is None:
        enl = estimate_enl(power)
    mean, var, _ = _local_moments(power, size)
    cu2 = 1.0 / enl
    with np.errstate(divide="ignore", invalid="ignore"):
        ci2 = var / (mean * mean)
        weight = np.clip(1.0 - cu2 / ci2, 0.0, 1.0)
    out = mean + weight * (power - mean)
    out = np.where(np.isfinite(power), out, np.nan)
    return out.astype(np.float32), float(enl)


def cross_pol_ratio_db(hh_db: np.ndarray, hv_db: np.ndarray) -> np.ndarray:
    """HV/HH ratio in dB: higher for volume scattering (vegetation), lower for surfaces."""
    return (hv_db - hh_db).astype(np.float32)
