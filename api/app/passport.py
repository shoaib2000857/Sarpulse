"""Change Passport: assemble labelled evidence for one location.

Separates Observed (scene values), Derived (classification), Context (ancillary
data) and Hypothesis (interpretation) so no claim is presented as more certain
than its source.
"""

import math

from .schemas import (
    Analysis,
    ChangePassport,
    ContextRecord,
    EvidenceItem,
    EvidenceLabel,
    SamplePoint,
    Scene,
)

STEEP_SLOPE_DEG = 10.0
FAR_SAMPLE_KM = 1.0

HYPOTHESES = {
    "water_gained": "Decrease in backscatter is consistent with new open water (specular reflection). "
    "Wind roughening, soil moisture or crop changes can produce similar signals.",
    "water_lost": "Increase in backscatter is consistent with water receding. Vegetation growth or "
    "wind-roughened water can also raise backscatter.",
    "stable_water": "Persistently low backscatter is consistent with permanent open water.",
    "stable_land": "No significant change in backscatter between the two acquisitions.",
    "ambiguous": "Signal change is inconclusive; needs review against independent evidence.",
}


def distance_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Equirectangular approximation; fine for distances within one site."""
    kx = 111.32 * math.cos(math.radians((lat1 + lat2) / 2))
    return math.hypot((lon2 - lon1) * kx, (lat2 - lat1) * 110.57)


def nearest_sample(samples: list[SamplePoint], lon: float, lat: float) -> tuple[SamplePoint, float]:
    best = min(samples, key=lambda s: distance_km(lon, lat, s.lon, s.lat))
    return best, distance_km(lon, lat, best.lon, best.lat)


def _delta(a: float | None, b: float | None) -> float | None:
    return None if a is None or b is None else round(b - a, 2)


def build_passport(
    site_id: str,
    lon: float,
    lat: float,
    analysis: Analysis,
    scenes: list[Scene],
    context: list[ContextRecord],
    sample: SamplePoint,
    sample_distance_km: float,
) -> ChangePassport:
    by_id = {s.scene_id: s for s in scenes}
    before = by_id.get(analysis.before_scene_id)
    after = by_id.get(analysis.after_scene_id)

    evidence = [
        EvidenceItem(
            label=EvidenceLabel.observed,
            statement="Radar backscatter (gamma-0, dB) at the nearest analysed sample.",
            values={
                "before_hh_db": sample.before_hh_db,
                "after_hh_db": sample.after_hh_db,
                "delta_hh_db": _delta(sample.before_hh_db, sample.after_hh_db),
                "before_hv_db": sample.before_hv_db,
                "after_hv_db": sample.after_hv_db,
                "delta_hv_db": _delta(sample.before_hv_db, sample.after_hv_db),
                "before_acquired_utc": before.acquired_at_utc.isoformat() if before else None,
                "after_acquired_utc": after.acquired_at_utc.isoformat() if after else None,
                "sample_distance_km": round(sample_distance_km, 3),
                "valid": sample.valid,
            },
            source=f"{analysis.before_scene_id} -> {analysis.after_scene_id}",
        ),
        EvidenceItem(
            label=EvidenceLabel.derived,
            statement=f"Classified as '{sample.change_class}' by {analysis.threshold_method}.",
            values={
                "change_class": sample.change_class,
                "processing_version": analysis.processing_version,
                "validation_status": analysis.validation_status,
            },
            source="science/analysis pipeline",
        ),
    ]
    for c in context:
        head = f"{c.kind}: {c.value} {c.units or ''}".strip()
        evidence.append(
            EvidenceItem(
                label=EvidenceLabel.context,
                statement=f"{head}. {c.caveat}",
                values=c.model_dump(mode="json", exclude={"data_status"}),
                source=c.source,
            )
        )
    evidence.append(
        EvidenceItem(
            label=EvidenceLabel.hypothesis,
            statement=HYPOTHESES.get(sample.change_class, HYPOTHESES["ambiguous"]),
        )
    )

    warnings: list[str] = []
    if before and after and before.maturity != after.maturity:
        warnings.append("Scenes have different processing maturity; change may be a processing artifact.")
    if not sample.valid:
        warnings.append("Sample falls in a masked / invalid-data area.")
    if sample.slope_deg is not None and sample.slope_deg > STEEP_SLOPE_DEG:
        warnings.append(f"Steep terrain ({sample.slope_deg} deg): layover/shadow artifacts likely.")
    if sample_distance_km > FAR_SAMPLE_KM:
        warnings.append(f"Nearest analysed sample is {sample_distance_km:.1f} km away.")

    return ChangePassport(
        site_id=site_id,
        lon=lon,
        lat=lat,
        before_scene_id=analysis.before_scene_id,
        after_scene_id=analysis.after_scene_id,
        change_class=sample.change_class,
        evidence=evidence,
        limitations=warnings + list(analysis.limitations),
        provenance=analysis.provenance,
        data_status=analysis.data_status,
    )
