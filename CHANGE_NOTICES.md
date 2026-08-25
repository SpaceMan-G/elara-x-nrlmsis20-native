# Change Notices

## 2026-08-25 — Initial controlled repository extraction

- Extracted only the exact accepted NRLMSIS 2.0 namespace files.
- Preserved source bytes and recorded every SHA-256 identity.
- Excluded `ui.py`, full Elara X, official Fortran, parameter payloads, and oracle payloads.
- Added metadata-only M18 equivalence evidence and independent repository tests.
- Set development version `0.1.0.dev0`; no final tag or release was created.

## 2026-08-25 — M02A public resource-boundary correction

- Removed the private Elara X controlled-workspace fallback from the standalone `nrlmsis20` resource resolver.
- Preserved explicit/external verified `msis21.parm` resolution only.
- Private accepted `resources.py` SHA-256: `82dc6160b6d28bd5d9752b681675d6d7ac39bcb1537a2fbe02615b79236aa905`.
- Public repository `resources.py` SHA-256: `eb6d32980be7d3c224d78d68ee7b4b1878364f6c349edd816876cb0958299660`.
- No official parameter payload is redistributed.
