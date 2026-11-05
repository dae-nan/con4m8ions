#!/usr/bin/env python3
"""Single deterministic rebuild of every generated artefact.

  docs/reference/isda/text/*.txt ──► cdu-ps-isda-2026-mapping.xlsx        (all sheets)
  curated tables in scripts/     ──► cdu-ps-fxo-deliverable-payload-mocks.xlsx (all sheets,
                                     incl. Prototype_Trade_Book + Prototype_Sim)
                                 ──► prototype/data/**/*.json + prototype/routes.json

Same inputs give byte-identical outputs. Never edit the workbooks by hand; change the
generators and rerun. Then run scripts/check_prototype_sync.py.

Run: .venv/bin/python scripts/build.py
"""
from __future__ import annotations

import io
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_prototype_data as sim_data  # noqa: E402
import generate_fxo_payload_mocks as mocks  # noqa: E402
import generate_phase1_mapping as mapping  # noqa: E402
import prototype_sim as sim  # noqa: E402

FIXED_TIME = datetime(2026, 1, 1)
STAMP = b"2026-01-01T00:00:00Z"


def build_workbooks():
    mapping_wb = mapping.build_workbook(mapping.PDF_TXT.read_text(encoding="utf-8"))
    mocks_wb = mocks.build_workbook()
    sim_data.add_sim_sheets(mocks_wb)
    return mapping_wb, mocks_wb


def save_deterministic(wb, path: Path) -> None:
    wb.properties.creator = "scripts/build.py"
    wb.properties.created = FIXED_TIME
    wb.properties.modified = FIXED_TIME
    buf = io.BytesIO()
    wb.save(buf)
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as src, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
        for info in src.infolist():
            fixed = zipfile.ZipInfo(info.filename, date_time=FIXED_TIME.timetuple()[:6])
            fixed.compress_type = zipfile.ZIP_DEFLATED
            fixed.external_attr = 0o644 << 16
            body = src.read(info.filename)
            if info.filename == "docProps/core.xml":
                # openpyxl stamps dcterms:modified with the wall clock on every save
                body = re.sub(rb"(<dcterms:modified[^>]*>)[^<]*", rb"\g<1>" + STAMP, body)
            dst.writestr(fixed, body)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(out.getvalue())


def main():
    mapping_wb, mocks_wb = build_workbooks()
    save_deterministic(mapping_wb, sim.MAPPING_XLSX)
    save_deterministic(mocks_wb, sim.MOCKS_XLSX)
    n = sim_data.export(mocks_wb)
    rel = lambda p: p.relative_to(sim.REPO).as_posix()  # noqa: E731
    print(f"built {rel(sim.MAPPING_XLSX)}, {rel(sim.MOCKS_XLSX)}; exported {n} files to prototype/data/ + {rel(sim.ROUTES_JSON)}")


if __name__ == "__main__":
    main()
