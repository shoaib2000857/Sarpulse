from fastapi import APIRouter, Depends, HTTPException, Query

from ..passport import build_passport, nearest_sample
from ..schemas import Analysis, ChangePassport, ContextRecord, Scene, Site, TimeSeries
from ..store import NotFound, Store, get_store

router = APIRouter(prefix="/api/sites", tags=["sites"])


def _get(fn, *args):
    try:
        return fn(*args)
    except NotFound as e:
        raise HTTPException(status_code=404, detail=f"Not found: {e}") from e


@router.get("", response_model=list[Site])
def list_sites(store: Store = Depends(get_store)):
    return [store.site(s) for s in store.site_ids()]


@router.get("/{site_id}", response_model=Site)
def get_site(site_id: str, store: Store = Depends(get_store)):
    return _get(store.site, site_id)


@router.get("/{site_id}/scenes", response_model=list[Scene])
def get_scenes(site_id: str, store: Store = Depends(get_store)):
    return _get(store.scenes, site_id)


@router.get("/{site_id}/summary", response_model=Analysis)
def get_summary(site_id: str, store: Store = Depends(get_store)):
    return _get(store.analysis, site_id)


@router.get("/{site_id}/timeseries", response_model=TimeSeries)
def get_time_series(site_id: str, store: Store = Depends(get_store)):
    return _get(store.time_series, site_id)


@router.get("/{site_id}/evidence", response_model=list[ContextRecord])
def get_evidence(site_id: str, store: Store = Depends(get_store)):
    return _get(store.context, site_id)


@router.get("/{site_id}/passport", response_model=ChangePassport)
def get_passport(
    site_id: str,
    lon: float = Query(ge=-180, le=180),
    lat: float = Query(ge=-90, le=90),
    store: Store = Depends(get_store),
):
    site = _get(store.site, site_id)
    if not site.bbox.contains(lon, lat):
        raise HTTPException(status_code=422, detail="Point is outside the analysed site area.")
    samples = _get(store.samples, site_id)
    if not samples:
        raise HTTPException(status_code=404, detail="No analysed samples for this site.")
    sample, dist = nearest_sample(samples, lon, lat)
    return build_passport(
        site_id,
        lon,
        lat,
        _get(store.analysis, site_id),
        _get(store.scenes, site_id),
        _get(store.context, site_id),
        sample,
        dist,
    )
