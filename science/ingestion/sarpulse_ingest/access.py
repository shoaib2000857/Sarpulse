"""Open GCOV products: a local file if present, otherwise stream over HTTPS with Earthdata Login.

Streaming reads only the HDF5 chunks covering the AOI (NISAR products are written with
paged, chunked storage for cloud access), so the ~7 GB product is never fully downloaded.
Credentials come from ~/.netrc or EARTHDATA_USERNAME / EARTHDATA_PASSWORD
(or EARTHDATA_TOKEN); they are never written by this package.
"""

from contextlib import contextmanager
from pathlib import Path

from .catalog import CandidateScene

BLOCK_SIZE = 8 * 1024 * 1024


def local_opener(local_dir: Path):
    @contextmanager
    def open_local(c: CandidateScene):
        path = Path(local_dir) / f"{c.scene_id}.h5"
        if not path.is_file():
            raise FileNotFoundError(path)
        yield str(path)

    return open_local


def earthdata_opener(local_dir: Path | None = None):
    """Prefer an already-downloaded file in local_dir; otherwise stream from Earthdata Cloud."""
    fs = None

    @contextmanager
    def open_remote(c: CandidateScene):
        nonlocal fs
        if local_dir and (Path(local_dir) / f"{c.scene_id}.h5").is_file():
            yield str(Path(local_dir) / f"{c.scene_id}.h5")
            return
        if fs is None:
            import earthaccess
            try:
                auth = earthaccess.login(strategy="environment" if _env_creds() else "netrc")
            except Exception as err:
                raise PermissionError("Earthdata Login unavailable: configure ~/.netrc or local Earthdata environment variables") from err
            if not auth or not auth.authenticated:
                raise PermissionError("Earthdata Login failed: configure local Earthdata credentials")
            fs = earthaccess.get_fsspec_https_session()
        with fs.open(c.url, mode="rb", cache_type="blockcache", block_size=BLOCK_SIZE) as f:
            yield f

    return open_remote


def _env_creds() -> bool:
    import os

    return bool(os.environ.get("EARTHDATA_TOKEN") or (os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD")))
