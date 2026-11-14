"""Parse NISAR product (granule) names.

Convention (https://nisar-docs.asf.alaska.edu/gcov/#naming-convention):

NISAR_IL_PT_PROD_CYL_REL_P_FRM_MODE_POLE_S_StartDateTime_EndDateTime_CRID_A_C_LOC_CTR
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone

PROCESSING_TYPES = {"PR": "Production", "UR": "Urgent Response", "OD": "Science On-Demand"}
ORBIT_ACCURACY = {"P": "Precise", "M": "Medium", "N": "Near Real-Time", "F": "Forecast"}
COVERAGE = {"F": "Full", "P": "Partial"}


@dataclass(frozen=True)
class GranuleName:
    name: str
    instrument: str
    level: str
    processing_type: str
    product: str
    cycle: int
    track: int
    direction: str  # "ASCENDING" / "DESCENDING"
    frame: int
    mode: str  # bandwidth code, e.g. "4005" = 40 MHz primary + 5 MHz secondary
    polarization: str  # e.g. "DHDH" = dual-pol HH/HV on both bands
    source: str
    start: datetime
    end: datetime
    crid: str
    orbit_accuracy: str
    coverage: str
    location: str
    counter: int

    @property
    def primary_bandwidth_mhz(self) -> int:
        return int(self.mode[:2])

    def to_dict(self) -> dict:
        d = asdict(self)
        d["start"] = self.start.isoformat().replace("+00:00", "Z")
        d["end"] = self.end.isoformat().replace("+00:00", "Z")
        return d


def _utc(stamp: str) -> datetime:
    return datetime.strptime(stamp, "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)


def parse_granule_name(name: str) -> GranuleName:
    stem = name.removesuffix(".h5")
    parts = stem.split("_")
    if len(parts) != 18 or parts[0] != "NISAR":
        raise ValueError(f"Not a NISAR product name: {name!r}")
    (_, il, pt, prod, cyl, rel, p, frm, mode, pole, s, start, end, crid, a, c, loc, ctr) = parts
    if p not in ("A", "D"):
        raise ValueError(f"Unknown orbit direction {p!r} in {name!r}")
    return GranuleName(
        name=stem,
        instrument=il[0],
        level=il[1:],
        processing_type=pt,
        product=prod,
        cycle=int(cyl),
        track=int(rel),
        direction="ASCENDING" if p == "A" else "DESCENDING",
        frame=int(frm),
        mode=mode,
        polarization=pole,
        source=s,
        start=_utc(start),
        end=_utc(end),
        crid=crid,
        orbit_accuracy=a,
        coverage=c,
        location=loc,
        counter=int(ctr),
    )
