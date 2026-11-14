"""Read an AOI window from a NISAR L2 GCOV HDF5 product (local path or remote file object).

Dataset paths follow JPL D-102274 (NISAR L2 GCOV Product Specification, Rev F):
- /science/LSAR/identification/*                     product identification
- /science/LSAR/GCOV/grids/frequencyA/{HHHH,HVHV}     gamma-0 RTC backscatter, linear power, float32, NaN fill
- /science/LSAR/GCOV/grids/frequencyA/mask            0 invalid/partially focused, 1-5 valid sub-swath, 255 fill
- /science/LSAR/GCOV/grids/frequencyA/{x,y}Coordinates pixel-centre map coordinates (metres)
- /science/LSAR/GCOV/grids/frequencyA/projection      EPSG code
"""

from dataclasses import dataclass

import h5py
import numpy as np

IDENT = "/science/LSAR/identification"
GRIDS = "/science/LSAR/GCOV/grids/frequencyA"
NESB = "/science/LSAR/GCOV/metadata/calibrationInformation/frequencyA/noiseEquivalentBackscatter"

IDENT_FIELDS = (
    "granuleId",
    "productType",
    "productVersion",
    "productSpecificationVersion",
    "compositeReleaseId",
    "processingType",
    "processingDateTime",
    "zeroDopplerStartTime",
    "zeroDopplerEndTime",
    "orbitPassDirection",
    "lookDirection",
    "trackNumber",
    "frameNumber",
    "absoluteOrbitNumber",
    "radarBand",
    "isUrgentObservation",
    "isFullFrame",
    "isDithered",
    "isMixedMode",
    "diagnosticModeFlag",
    "hasInputDataException",
    "productDoi",
    "staticLayersDataAccess",
    "boundingPolygon",
)


def _scalar(value):
    if isinstance(value, bytes):
        return value.decode()
    if isinstance(value, np.ndarray):
        return [_scalar(v) for v in value.tolist()] if value.ndim else _scalar(value[()])
    if isinstance(value, np.generic):
        return value.item()
    return value


def read_identification(h5: h5py.File) -> dict:
    group = h5[IDENT]
    return {k: _scalar(group[k][()]) for k in IDENT_FIELDS if k in group}


@dataclass
class GcovGrid:
    epsg: int
    x: np.ndarray  # pixel-centre x, length = width
    y: np.ndarray  # pixel-centre y, length = height
    dx: float
    dy: float  # negative for north-up products
    polarizations: list[str]
    covariance_terms: list[str]


def read_grid(h5: h5py.File) -> GcovGrid:
    g = h5[GRIDS]
    x = g["xCoordinates"][()]
    y = g["yCoordinates"][()]
    dx = float(g["xCoordinateSpacing"][()]) if "xCoordinateSpacing" in g else float(x[1] - x[0])
    dy = float(g["yCoordinateSpacing"][()]) if "yCoordinateSpacing" in g else float(y[1] - y[0])
    proj = g["projection"]
    epsg = int(proj.attrs.get("epsg_code", proj[()]))
    return GcovGrid(
        epsg=epsg,
        x=x,
        y=y,
        dx=dx,
        dy=dy,
        polarizations=[_scalar(p) for p in g["listOfPolarizations"][()]] if "listOfPolarizations" in g else [],
        covariance_terms=[_scalar(t) for t in g["listOfCovarianceTerms"][()]] if "listOfCovarianceTerms" in g else [],
    )


@dataclass
class Window:
    row0: int
    row1: int
    col0: int
    col1: int

    @property
    def shape(self) -> tuple[int, int]:
        return (self.row1 - self.row0, self.col1 - self.col0)


def window_for_bounds(grid: GcovGrid, xmin: float, ymin: float, xmax: float, ymax: float, margin: int = 1) -> Window | None:
    """Smallest index window whose pixels cover [xmin, xmax] x [ymin, ymax]; None if no overlap."""
    half_x, half_y = abs(grid.dx) / 2, abs(grid.dy) / 2
    cols = np.nonzero((grid.x + half_x > xmin) & (grid.x - half_x < xmax))[0]
    rows = np.nonzero((grid.y + half_y > ymin) & (grid.y - half_y < ymax))[0]
    if cols.size == 0 or rows.size == 0:
        return None
    return Window(
        row0=max(int(rows.min()) - margin, 0),
        row1=min(int(rows.max()) + 1 + margin, grid.y.size),
        col0=max(int(cols.min()) - margin, 0),
        col1=min(int(cols.max()) + 1 + margin, grid.x.size),
    )


@dataclass
class GcovSubset:
    """Native-resolution AOI window. Backscatter is gamma-0 linear power (unitless)."""

    terms: dict[str, np.ndarray]
    valid: np.ndarray  # bool: GCOV mask in 1..5, finite and positive in every term
    number_of_looks: np.ndarray | None
    x: np.ndarray
    y: np.ndarray
    dx: float
    dy: float
    epsg: int
    receive_only_terms: list[str]


def read_subset(h5: h5py.File, grid: GcovGrid, window: Window, terms=("HHHH", "HVHV")) -> GcovSubset:
    g = h5[GRIDS]
    missing = [t for t in terms if t not in g]
    if missing:
        raise KeyError(f"Product lacks covariance terms {missing}; available: {grid.covariance_terms}")
    sl = (slice(window.row0, window.row1), slice(window.col0, window.col1))

    mask = g["mask"][sl]
    valid = (mask >= 1) & (mask <= 5)
    if "inputDataExceptionMask" in g:
        valid &= g["inputDataExceptionMask"][sl] == 0

    data, receive_only = {}, []
    for t in terms:
        ds = g[t]
        if any(str(_scalar(ds.attrs.get(a, "False"))) == "True" for a in ("isReceiveOnlyChannel1", "isReceiveOnlyChannel2")):
            receive_only.append(t)
        arr = ds[sl].astype(np.float32)
        valid &= np.isfinite(arr) & (arr > 0)
        data[t] = arr

    for arr in data.values():
        arr[~valid] = np.nan

    nlooks = g["numberOfLooks"][sl].astype(np.float32) if "numberOfLooks" in g else None
    return GcovSubset(
        terms=data,
        valid=valid,
        number_of_looks=nlooks,
        x=grid.x[window.col0 : window.col1],
        y=grid.y[window.row0 : window.row1],
        dx=grid.dx,
        dy=grid.dy,
        epsg=grid.epsg,
        receive_only_terms=receive_only,
    )


def noise_equivalent_backscatter_db(h5: h5py.File, pols=("HH", "HV")) -> dict[str, float]:
    """Median noise-equivalent backscatter (dB) per polarization over the whole product.

    Informational only: the spec gives it in linear DN^2 on a sparse grid; it flags
    where low HV returns (e.g. calm water) approach the instrument noise floor.
    """
    out = {}
    if NESB not in h5:
        return out
    group = h5[NESB]
    for p in pols:
        if p in group:
            vals = group[p][()]
            vals = vals[np.isfinite(vals) & (vals > 0)]
            if vals.size:
                out[p] = round(float(10 * np.log10(np.median(vals))), 2)
    return out
