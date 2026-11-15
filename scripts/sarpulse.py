"""Repository entry point for the SARPulse pipeline."""
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for rel in ("platform", "science/ingestion", "science/analysis", "api"):
    sys.path.insert(0, str(root / rel))

from sarpulse_platform.cli import main

raise SystemExit(main())
