"""Write tiny HDF5 files in the NISAR GCOV layout for tests.

SYNTHETIC/DEMO — NOT NASA OBSERVATIONS. Values are made up; the root attribute
`sarpulse_synthetic` makes the ingestion pipeline label every output as synthetic.
"""

import h5py
import numpy as np

from sarpulse_ingest.gcov import GRIDS, IDENT


def write_synthetic_gcov(
    path,
    granule: str,
    x_centres: np.ndarray,
    y_centres: np.ndarray,
    hh: np.ndarray,
    hv: np.ndarray,
    mask: np.ndarray,
    epsg: int = 32646,
    start: str = "2026-07-22T23:05:28.000000000",
    crid: str = "P05023",
) -> None:
    with h5py.File(path, "w") as f:
        f.attrs["sarpulse_synthetic"] = True
        ident = f.create_group(IDENT)
        for k, v in {
            "granuleId": granule,
            "productType": "GCOV",
            "compositeReleaseId": crid,
            "zeroDopplerStartTime": start,
            "orbitPassDirection": "Ascending",
            "trackNumber": np.uint32(40),
            "frameNumber": np.uint16(15),
        }.items():
            ident.create_dataset(k, data=v)
        g = f.create_group(GRIDS)
        g.create_dataset("xCoordinates", data=x_centres.astype(np.float64))
        g.create_dataset("yCoordinates", data=y_centres.astype(np.float64))
        g.create_dataset("xCoordinateSpacing", data=float(x_centres[1] - x_centres[0]))
        g.create_dataset("yCoordinateSpacing", data=float(y_centres[1] - y_centres[0]))
        proj = g.create_dataset("projection", data=np.uint32(epsg))
        proj.attrs["epsg_code"] = epsg
        g.create_dataset("listOfPolarizations", data=np.array([b"HH", b"HV"]))
        g.create_dataset("listOfCovarianceTerms", data=np.array([b"HHHH", b"HVHV"]))
        g.create_dataset("HHHH", data=hh.astype(np.float32), chunks=True)
        g.create_dataset("HVHV", data=hv.astype(np.float32), chunks=True)
        g.create_dataset("mask", data=mask.astype(np.uint8), chunks=True)
        g.create_dataset("numberOfLooks", data=np.full(hh.shape, 4.0, dtype=np.float32))
