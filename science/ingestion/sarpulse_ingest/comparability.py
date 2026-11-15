"""Group candidate GCOV products into stacks that can be compared over time.

Two acquisitions are only treated as comparable when they share viewing geometry
(track, direction, frame), radar mode (bandwidth, polarization), processing type and
software release (CRID). Differences in data maturity or orbit accuracy do not split
a stack but are reported as warnings.
"""

from collections import defaultdict
from dataclasses import dataclass, field

from .catalog import CandidateScene

REQUIRED_TERMS = ("HH", "HV")


@dataclass
class Stack:
    key: dict
    scenes: list[CandidateScene]
    warnings: list[str] = field(default_factory=list)

    @property
    def stack_id(self) -> str:
        k = self.key
        return f"T{k['track']:03d}{k['direction'][0]}_F{k['frame']:03d}_{k['mode']}_{k['polarization']}_{k['processing_type']}_{k['crid']}"

    def to_dict(self) -> dict:
        return {
            "stack_id": self.stack_id,
            "key": self.key,
            "n_dates": len(self.scenes),
            "dates": [s.start_utc[:10] for s in self.scenes],
            "warnings": self.warnings,
            "scenes": [s.scene_id for s in self.scenes],
        }


def stack_key(s: CandidateScene) -> tuple:
    return (s.track, s.direction, s.frame, s.mode, s.polarization, s.processing_type, s.crid)


def _dedupe(scenes: list[CandidateScene]) -> tuple[list[CandidateScene], list[str]]:
    """Keep one product per acquisition: the highest product counter (latest reprocessing)."""
    by_start: dict[str, CandidateScene] = {}
    dropped: list[str] = []
    for s in sorted(scenes, key=lambda s: s.counter):
        if s.start_utc in by_start:
            dropped.append(by_start[s.start_utc].scene_id)
        by_start[s.start_utc] = s
    return sorted(by_start.values(), key=lambda s: s.start_utc), dropped


def build_stacks(candidates: list[CandidateScene], min_dates: int = 2) -> list[Stack]:
    groups: dict[tuple, list[CandidateScene]] = defaultdict(list)
    for s in candidates:
        if all(t in s.main_band_polarizations for t in REQUIRED_TERMS):
            groups[stack_key(s)].append(s)

    stacks = []
    for key, members in groups.items():
        scenes, dropped = _dedupe(members)
        if len(scenes) < min_dates:
            continue
        warnings = []
        if dropped:
            warnings.append(f"Superseded reprocessed duplicates ignored: {', '.join(dropped)}")
        maturities = sorted({s.maturity for s in scenes})
        if len(maturities) > 1:
            warnings.append(f"Mixed data maturity in stack: {', '.join(maturities)}")
        accuracies = sorted({s.orbit_accuracy for s in scenes})
        if len(accuracies) > 1:
            warnings.append(f"Mixed orbit-ephemeris accuracy codes: {', '.join(accuracies)} (geolocation may differ slightly)")
        if any(s.coverage != "F" for s in scenes):
            warnings.append("Some products are partial-frame; AOI coverage must be checked per scene")
        track, direction, frame, mode, pol, ptype, crid = key
        stacks.append(
            Stack(
                key={
                    "track": track,
                    "direction": direction,
                    "frame": frame,
                    "mode": mode,
                    "polarization": pol,
                    "processing_type": ptype,
                    "crid": crid,
                },
                scenes=scenes,
                warnings=warnings,
            )
        )
    # Most dates first, then prefer production over urgent-response processing.
    return sorted(stacks, key=lambda st: (-len(st.scenes), st.key["processing_type"] != "PR", st.stack_id))
